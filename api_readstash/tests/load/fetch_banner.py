from locust import HttpUser, task, constant


class BannerUser(HttpUser):
    wait_time = constant(0)  # Short wait time to aim for high RPS

    @task
    def fetch_menu_and_images(self):
        self.client.get("/backendmenu/api/v1/menus/get-html-content/2b2bf4ea-7d67-45b0-ad24-01a4c0fd75be")
        self.client.get("/backendmenu/api/v1/files/defe915a-cc72-4f5a-b52c-c3eed0f7c918")
        self.client.get("/backendmenu/api/v1/files/efe2404f-26ce-4f38-8e98-a92638ef019f")
