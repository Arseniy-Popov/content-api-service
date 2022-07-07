Run for development
```
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up 
```

Run for production
```
docker-compose -f docker-compose.yaml up 
```

Spin up containers to run functional tests locally, outside of containers
```
docker-compose -f docker-compose.test.yaml up 
```

Run functional tests in containers
```
docker-compose -f docker-compose.test.yaml -f docker-compose-tests.yaml up
```

api: https://github.com/Arseniy-Popov/Async_API_sprint_1  
etl: https://github.com/Arseniy-Popov/new_admin_panel_sprint_3 