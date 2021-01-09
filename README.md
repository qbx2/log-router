# Log Router
For fluent-bit tcp output

Currently log record is routed to slack

## Deploy
Create secret named log-router-config with key webhook-url to <your webhook url>

```
git clone https://github.com/qbx2/log-router
kubectl apply -k log-router
```

## Fluent-bit config
```
[OUTPUT]
    Name tcp
    Host log-router
    Format json_lines
```
