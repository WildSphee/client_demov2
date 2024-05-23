streamlit FE for compliant demo

# setup:

1. .env
```
NEXTGPT_BACKEND_PORT=<PORT NO>
NEXTGPT_API_KEY=<>
```

2. Ensure NEXTgpt backend (v1) is running and pointed to
3. Start streamlit: streamlit run main.py


V1 – Experts give their own point of view given role-specific KPIs, in paragraph format
![alt text](docs/1.png)
![alt text](docs/2.png)
![alt text](docs/3.png)


V2 – All experts given the same metrics, consolidated into the same table
![alt text](docs/image.png)
![alt text](docs/image-1.png)
![alt text](docs/image-2.png)

V3 – Use LLM to delegate task to each expert, and consolidate them together
![alt text](docs/image-3.png)
![alt text](docs/image-4.png)

V3 Final results:
![alt text](docs/image-5.png)
![alt text](docs/image-6.png)