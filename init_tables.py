from init_app import create_app

app, dynamo = create_app()

with app.app_context():
    dynamo.create_all()


cities = ['Bengaluru', 'Gurgaon', 'Mumbai', 'Pune', 'Chennai', 'Noida']

i = 0
for city in cities:
    dynamo.tables['cities'].put_item(Item={
        'id': i,
        'name': city,
    })
    print(f'Added {city} to cities table')

    dynamo.tables['days'].put_item(Item={
        'id': i,
        'monday': 0,
        'tuesday': 0,
        'wednesday': 0,
        'thursday': 0,
        'friday': 0,
        'saturday': 0,
        'sunday': 0,
    })
    print(f'Added day to days table')
    i += 1

