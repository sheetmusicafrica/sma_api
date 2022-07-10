"""
  Prepare payout
  send payout
  get payout status
  ----------------------
  deduct payout charges from our account
  get payout status
  retry payout
  withdrawl our money
"""
from django.utils import timezone
from django.db.models import Q

from composer.models import ComposerProfile,UserPaymentHistory,ComposerAccount
from sheet_music_africa.settings import FLUTTER_WAVE_COUNTRIES, PAYMENT_LANDMARK, PAYMENT_SECRET_KEY, FLUTTER_URL
from .models import BatchPayout


import requests

payout_per_batch = 40
currency = "USD"
flutter_callback = ""

def get_composers():
  """
     return list of compsers that payment has not been made to
  """
  today = timezone.now().date()
  all_composers = ComposerProfile.objects.filter(current_sales__gte=PAYMENT_LANDMARK).exclude(country__in=FLUTTER_WAVE_COUNTRIES)
  payout_batches = BatchPayout.objects.filter(Q(month=today.month)&Q(year=today.year))

  
  for batch in payout_batches:
    all_composers = all_composers.exclude(batch.composers_paid_to)

  return [all_composers,payout_batches.count()+1]


def prepare_and_make_payout():
  batch_data = get_composers()
  composers = batch_data[0]

  while True:

    if composers.count() == 0:
      print("Payout completed")
      break

    item_count = 0
    data = [] #payout_data

    batch = BatchPayout()
    batch.provider = "flutterwave"
    batch.date = timezone.now().date()
    batch.batch_number = batch_data[1]
    batch.save()
    batch.set_month_and_year()

    batch_info = "M:%s-Y:%s-N:%d-I:%d-IT:"%(batch.month,batch.year,batch.batch_number,batch.id)

    total_amount = 0

    for composer in composers:
      
      if item_count == payout_per_batch:
        break
      else:
        item_count += 1

      composer_account = ComposerAccount.objects.get(composer=composer)
      amount = float(composer.current_sales)

      #create payoutLog here
      payout = UserPaymentHistory()
      payout.user = composer.user
      payout.price = amount
      payout.payment_type = "payout"
      payout.save()

      total_amount += amount
      data.append({
        "bank_code": composer_account.bank_code,
        "account_number": composer_account.account_number,
        "amount": amount,
        "narration": "Sheet music africa payout.",
        "currency": currency,
        "reference": batch_info+"_%d" % payout.id,
        "debit_currency": currency
      })

      batch.composers_paid_to.add(composer)

    batch.amount = total_amount
    batch.save()

    payout_data = {
      "bulk_data":data,
      "title": "Sheet Music Africa Composers payout"
    }

    make_payout(batch,payout_data)
    continue



def make_payout(batch,data):
  headers = {"Content-Type": "Application/json","Authorization":'Bearer %s' % PAYMENT_SECRET_KEY}

  print("my data === ", data)
  r = requests.post(url="%stransfers" % FLUTTER_URL, json=data, headers=headers)
  response = r.json()
  print(response)

  try:
    status = response['status']
  except:
    #payout failed
    #notify developers
    pass
