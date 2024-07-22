import csv
import random
from faker import Faker

fake = Faker()

# List of broad and niche backgrounds
backgrounds = [
    "Software Engineering", "Data Science", "Marketing", "Finance", "Human Resources",
    "Quantum Computing", "Bioinformatics", "Ethnobotany", "Astrobiology", "Glaciology",
    "Cryptocurrency", "Artificial Intelligence", "Sustainable Energy", "Graphic Design", "Journalism",
    "Nanotechnology", "Paleoclimatology", "Cybersecurity", "Urban Planning", "Neuroscience",
    "Organic Farming", "Space Law", "Robotics", "Marine Archaeology", "Geopolitics",
    "3D Printing", "Blockchain", "Virtual Reality", "Augmented Reality", "Internet of Things",
    "Cognitive Psychology", "Astrophysics", "Biomimicry", "Cryptography", "Synthetic Biology"
]

data = []
for i in range(200):
    background = random.choice(backgrounds)
    username = fake.user_name()
    display_name = fake.name()
    points = random.randint(0, 10000)
    domain = []
    social_link = f"https://{fake.domain_name()}/{username}"

    bio = f"Expert in {background} with {random.randint(1, 20)} years of experience."
    works = f"Published {random.randint(1, 50)} papers and worked on {random.randint(1, 10)} major projects in {background}."

    data.append([
        username, display_name, background, points, domain, "website", social_link, bio, works
    ])

with open('sample_dataset.csv', 'w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(["username", "display_name", "background", "points",
                    "domain", "social_type", "social_link", "bio", "works"])
    writer.writerows(data)

print("CSV file 'sample_dataset.csv' has been generated with 200 records.")
