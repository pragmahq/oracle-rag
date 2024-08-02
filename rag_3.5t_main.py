import os
import psycopg2
import openai
from typing import List, Dict
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')

# Database connection function
def connect_to_db():
    return psycopg2.connect(
        dbname=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT')
    )

# Function to get user data from the database
def get_user_data() -> List[Dict]:
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT id, username, display_name, bio, works FROM pragma_accounts WHERE visibility = true")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return [{"id": user[0], "username": user[1], "display_name": user[2], "bio": user[3], "works": user[4]} for user in users]

# Function to use GPT-3 to analyze and rank users
def rank_users_for_project(project_description: str, users: List[Dict]) -> List[Dict]:
    ranked_users = []
    
    for user in users:
        messages = [
            {"role": "system", "content": "You are an AI assistant that helps match users to projects based on their bio and works."},
            {"role": "user", "content": f"""
            Project Description: {project_description}

            User Information:
            Username: {user['username']}
            Display Name: {user['display_name']}
            Bio: {user['bio']}
            Works: {user['works']}

            Based on the project description and the user's bio and works, rate the user's suitability for the project on a scale of 1 to 10, where 10 is the most suitable. Provide a brief explanation for the rating.

            Respond in the following format:
            Rating: [Your rating]
            Explanation: [Your explanation]
            """}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=messages,
            max_tokens=150,
            n=1,
            stop=None,
            temperature=0.5,
        )

        response_content = response.choices[0].message['content'].strip()
        rating_text = response_content.split('\n')
        rating = int(rating_text[0].split(':')[1].strip())
        explanation = rating_text[1].split(':')[1].strip()

        ranked_users.append({
            "id": user['id'],
            "username": user['username'],
            "display_name": user['display_name'],
            "rating": rating,
            "explanation": explanation
        })

    return sorted(ranked_users, key=lambda x: x['rating'], reverse=True)

# Main function to find the best person for a project
def find_best_person_for_project(project_description: str, num_recommendations: int = 3) -> List[Dict]:
    users = get_user_data()
    ranked_users = rank_users_for_project(project_description, users)
    return ranked_users[:num_recommendations]

# Example usage
if __name__ == "__main__":
    project_description = "Develop a machine learning model for sentiment analysis on social media data"
    best_matches = find_best_person_for_project(project_description)
    
    print("Best matches for the project:")
    for i, match in enumerate(best_matches, 1):
        print(f"{i}. Username: {match['username']}")
        print(f"   Display Name: {match['display_name']}")
        print(f"   Rating: {match['rating']}/10")
        print(f"   Explanation: {match['explanation']}")
        print()