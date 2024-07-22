from typing import List

class Domain:
    def __init__(self, domain_id: str, name: str):
        self.domain_id = domain_id
        self.name = name

class SocialLink:
    def __init__(self, username: str, type: str, label: str, link: str):
        self.username = username
        self.type = type
        self.label = label
        self.link = link

class PragmaAccount:
    def __init__(self, visibility: bool, discord_id: int, username: str, display_name: str,
                 points: int, account_secret: str, domains: List[Domain], social_links: List[SocialLink],
                 bio: str, works: str):
        self.visibility = visibility
        self.discord_id = discord_id
        self.username = username
        self.display_name = display_name
        self.points = points
        self.account_secret = account_secret
        self.domains = domains
        self.social_links = social_links
        self.bio = bio
        self.works = works
