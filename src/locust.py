from locust import HttpUser, task, between
import random

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)  # Wait between 1 and 3 seconds between tasks

    @task()  
    def get_teams_endpoint(self):
        self.client.get("/api/teams", verify=False) 

    @task()
    def get_players_endpoint(self):
        self.client.get("/api/players", verify=False) 

    @task()
    def get_teams_players_endpoint(self):
        self.client.get("/api/teams/players", verify=False)
