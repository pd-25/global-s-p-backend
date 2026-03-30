# Read input
A = input().strip()
P = input().strip()

# Count positions where both are same (both 0 or both 1)
count = 0
for i in range(len(A)):
    if A[i] == P[i]:
        count += 1

# Print result
print(count)


#Frakset question

import requests

def bestInGenre(genre):
    base_url = "https://jsonmock.hackerrank.com/api/tvseries"
    
    # Make the first request to find out how many pages of data exist
    initial_response = requests.get(f"{base_url}?page=1").json()
    total_pages = initial_response['total_pages']
    
    best_name = None
    highest_rating = -1.0
    
    # Iterate through all available pages
    for page in range(1, total_pages + 1):
        res = requests.get(f"{base_url}?page={page}").json()
        
        for show in res['data']:
            # The genre field is a comma-separated string. 
            # We split it and strip whitespace to ensure accurate matching.
            show_genres = [g.strip() for g in show.get('genre', '').split(',')]
            
            # If our target genre is in this show's list of genres
            if genre in show_genres:
                current_rating = show.get('imdb_rating', 0)
                current_name = show.get('name', '')
                
                # Check if we have a new highest rating
                if current_rating > highest_rating:
                    highest_rating = current_rating
                    best_name = current_name
                # If there's a tie, fall back to alphabetical order
                elif current_rating == highest_rating:
                    if best_name is None or current_name < best_name:
                        best_name = current_name
                        
    return best_name