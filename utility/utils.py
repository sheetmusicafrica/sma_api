from musicStore.models import Genre


def getName(name):
    # removing " from start and end
    # " was added by JSON.stringiy() in frontend

    return name[1:len(name)-1]

def processNewGenre(data):
    data = data.split(",")

    for col in data:
        col_data = col.split(":")
        if col_data[1] != "null":
            Genre(
                name=getName(col_data[1]),
                is_instrument = getName(col_data[0]) == "instrument"
            ).save()

    
