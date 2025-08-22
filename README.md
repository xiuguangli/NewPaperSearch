1.mongodb：
```yml
services:
    mongodb:
        image: mongo
        container_name: mongodb
        restart: always
        ports:
        - "27017:27017"
        volumes:
        - ./data:/data/db
```

2.import data
需要 data 数据
```bash
python get_data/database/add_to_mongodb.py
```

3.前后端启动
```bash
docker-compose up -d
```