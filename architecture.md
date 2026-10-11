# Architecture notes

```text
Client / load tester
        |
        v
Kubernetes Service (ClusterIP)
        |
        v
Deployment: autoscale-demo (2 to 10 Pods)
        |
        +--> /healthz and /readyz probes
        +--> /work endpoint to create bounded CPU work for a demo

Metrics Server --> HPA controller --> adjusts Deployment replica count
GitHub Actions --> builds image --> GitHub Container Registry (GHCR)
```

## Scaling flow

1. Requests to `/work?iterations=250000` use CPU for a short, bounded calculation.
2. Kubernetes Metrics Server provides CPU usage metrics.
3. The Horizontal Pod Autoscaler targets average CPU utilization of 50% of container CPU requests and changes replica count between 2 and 10.
4. Observe with `kubectl get hpa,pods -n autoscale-demo -w`.

This is a learning/demo scaffold. Add monitoring, alerts, ingress/TLS, deployment environments, and cloud-specific infrastructure when you develop it further.
