from django.utils import timezone
from django.db.models import Q

from sheet_music_africa.settings import FLUTTER_WAVE_COUNTRIES, PAYMENT_LANDMARK, PAYMENT_SECRET_KEY, FLUTTER_URL
import requests
from requests.auth import HTTPBasicAuth

from composer.models import UserPaymentHistory, ComposerProfile, ComposerAccount, UserPaymentLog

from .models import BatchPayout

# Single payout
# batch payout
# retries
# get payout rates

# paypal and flutterwave

# function
"""
    run payout,
    generate payout data,
    check payout state,
    make payout and retry payout
"""


def getCharges(amount):
    headers = {
        'Authorization':'Bearer %s' % PAYMENT_SECRET_KEY
    }


    r = requests.get(url="%stransfers/fee" % FLUTTER_URL, params={'amount':amount, "currency": "USD"}, headers=headers)

    return r.json()


def check_payout_status(payout_id):
    pass


def generate_payout_id(payout_provider):
    """
       here we generate payout id
    """
    print(payout_provider, "------------------paying out -----------------")
    today = timezone.now().date()
    this_month_batch_count = BatchPayout.objects.filter(
        Q(month=today.month) & Q(year=today.year)
        & Q(provider=payout_provider)).count()

    try:
        last_batch = BatchPayout.objects.get(
            Q(month=today.month) & Q(year=today.year)
            & Q(provider=payout_provider) &
            Q(batch_number=this_month_batch_count+1))

    except BatchPayout.DoesNotExist:
        last_batch = BatchPayout()
        last_batch.provider = payout_provider
        last_batch.date = timezone.now().date()
        last_batch.batch_number = this_month_batch_count+1

        last_batch.save()
        last_batch.set_month_and_year()

    # generating new payout batch, if last batch is full
    if last_batch.full == True:
        payout_batch = BatchPayout()
        payout_batch.provider = payout_provider
        payout_batch.date = timezone.now().date()
        payout_batch.batch_number = this_month_batch_count+1

        payout_batch.save()
        payout_batch.set_month_and_year()

        return payout

    return last_batch


def make_payout(payout_data, payout_provider, batch_id, access):
    # we need to check if payout has been made in the past so as not to make payment twice
    """
       payout_provider is either flutterwave or paypal
    """
    headers = {"Content-Type": "Application/json"}
    data = dict()

    if(payout_provider == "paypal"):
        url = PAYPAL_PAYOUT_URL
        headers["Authorization"] = "Bearer %s" % access

        data["sender_batch_header"] = {
            "sender_batch_id": batch_id,
            "recipient_type": "EMAIL",
            "email_subject": "You have a payout!",
            "email_message": "You have received a payout! Thanks for using our service!"
        }

        data["items"] = payout_data

    else:
        headers['Authorization'] = 'Bearer %s' % PAYMENT_SECRET_KEY
        url = "%stransfers" % FLUTTER_URL
        data["bulk_data"] = payout_data
        data["title"] = "Composer payout"

    print("my data === ", data)
    r = requests.post(url=url, json=data, headers=headers)
    print(r.json())

    data = r.json()
    if payout_provider == "paypal":
        if data["batch_status"] == "PENDING":
            return "processing"
        else:
            # check if we've exceeded our max retry here
            return "retry"
    else:
        try:
            if data["status"] == "success":
                return "processing"
        except:
            # check if we've exceeded our max retry here
            return "retry"


def process_payout(payout_provider, composer, batch_payout_id):
    # then we need to create payout log to log payment by months - done
    # then for paypal we need to break the payout transaction to be less than $15k per payout -done
    currency = "USD"
    note = "POSPYO001"
    flutter_callback = "http://localhost:3000"
    data = []
    today = timezone.now().date()
    batch_payout_id = batch_payout_id
    account = ComposerAccount.objects.get(composer=composer)

    # create payout user log here
    amount = composer.current_sales
    user_payout_log = UserPaymentLog()
    user_payout_log.user = composer.user
    user_payout_log.price = amount
    user_payout_log.log_type = "payout"
    user_payout_log.save()

    payout_id = user_payout_log.id

    if(payout_provider == "paypal"):
        data = {
            "amount": {
                "value": str(amount),
                "currency": currency
            },
            "note": note,
            "sender_item_id": batch_payout_id+"_%d" % payout_id,
            "receiver": account.email
        }

    else:
        data = {
            "bank_code": account.bank_code,
            "account_number": account.account_number,
            "amount": float(amount),
            "narration": "Sheet music africa payout.",
            "currency": currency,
            "reference": batch_payout_id+"_%d" % payout_id,
            # "callback_url": flutter_callback,
            "debit_currency": currency
        }

    return data


def get_paypal_access_token(provider):

    if provider == "paypal":
        headers = {
            "Content-Type": "Application/json",
            "Accept": "application/json",
            "Accept-Language": "en_US"
        }
        data = {"grant_type": "client_credentials"}
        r = requests.post(url=PAYPAL_SANDBOX_URL, auth=HTTPBasicAuth(
            PAYPAL_CLIENT_ID, PAYPAL_SECRET_KEY), data=data, headers=headers)

        data = r.json()
        print(data)

        return data['access_token'],
    return None


def break_payouts_into_batches_and_get_next_batch(composers, payout_provider):
    batch_amount_max = 15000
    amount_addded_to_payout_item = 0
    payout_item = []
    today = timezone.now().date()

    current_batch = generate_payout_id(
        payout_provider)

    batch_id = "payout-"+str(today)+":%d" % current_batch.id

    for composer in composers:

        if amount_addded_to_payout_item+composer.current_sales < batch_amount_max:
            payout_item.append(process_payout(
                payout_provider, composer, batch_id))
            current_batch.composers_paid_to.add(composer)
            current_batch.save()
            amount_addded_to_payout_item += composer.current_sales

        else:
            # work on this part
            current_batch.amount = amount_addded_to_payout_item
            current_batch.full = True
            current_batch.save()

            # has_more = True
            return [payout_item, True, current_batch.composers_paid_to, batch_id]

    # has_more = False
    return [payout_item, False, [], batch_id]


def start_payout(payout_provider=None):
    all_composers = ComposerProfile.objects.filter(
        current_sales__gte=PAYMENT_LANDMARK)

    # filter out composers withou payment account

    payment_accounts = [
        composer.id for composer in ComposerAccount.objects.all()]
    all_composers = all_composers.filter(pk__in=payment_accounts)

    payouts = {
        'flutterwave': all_composers.exclude(country__in=FLUTTER_WAVE_COUNTRIES),
        'paypal': all_composers.filter(country__in=FLUTTER_WAVE_COUNTRIES)
    }

    for payout in payouts:
        if payouts[payout].count() != 0:
            while True:
                current_composers = payouts[payout]
                payout_provider = payout

                payout_batch = break_payouts_into_batches_and_get_next_batch(
                    current_composers, payout_provider)

                batch_id = payout_batch[3]

                payout_response = make_payout(
                    payout_batch[0], payout_provider, batch_id, get_paypal_access_token(payout_provider))

                if payout_response == "processing":
                    # deduct value from users here
                    # log everything
                    # get payment log and use it to perform deduction
                    for composer in current_composers:
                        composer.current_sales = 0
                        composer.save()

                elif payout_response == "retry":
                    # retry a max of 3 times, if it still fails contact developers
                    pass

                else:
                    # notify developers by email that payout failed
                    pass

                if payout_batch[1] == True:
                    # removing last batch composer from next batch
                    composers_paid_to = payout_batch[2]
                    current_composers = current_composers.exclude(
                        composers_paid_to)
                    continue
                else:
                    break

    print("payout Completed")


def withdrawlRevenue(account, amount):
    # call make_payout for single payout
    pass
