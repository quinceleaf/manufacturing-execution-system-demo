import random

from celery import shared_task


@shared_task(name="generate_random_number")
def random_generate():
    random_value = random.randint(0, 1000) / random.randint(1, 1000)
    print(f"Random value is: {random_value}")