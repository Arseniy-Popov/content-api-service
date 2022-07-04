Run for development
```
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml build 
docker-compose -f docker-compose.yaml -f docker-compose.dev.yaml up 
```

Run for production
```
docker-compose -f docker-compose.yaml build 
docker-compose -f docker-compose.yaml up 
```

api: https://github.com/Arseniy-Popov/Async_API_sprint_1  
etl: https://github.com/Arseniy-Popov/new_admin_panel_sprint_3 