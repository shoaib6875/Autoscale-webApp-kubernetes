# Autoscale Cloud — Kubernetes HPA Demo

A starter project demonstrating containerized deployment, Kubernetes horizontal pod autoscaling, and a small load-testing workflow. This repository is a scaffold to build on—not a claim that a cloud deployment is already running.

## What is included

- Small Python HTTP app with health/readiness endpoints and bounded CPU work at `/work`.
- Dockerfile and local Docker Compose setup.
- Kubernetes Namespace, Deployment, Service, and Horizontal Pod Autoscaler (HPA).
- Load-test script built with Python's standard library.
- GitHub Actions workflow to build and publish the image to GitHub Container Registry (GHCR).

## Run locally

Requirements: Python 3.10+ or Docker.

### Option A — Python

```bash
python app.py
```

Open `http://localhost:8080/` or `http://localhost:8080/healthz`.

### Option B — Docker Compose

```bash
docker compose up --build
```

Then visit `http://localhost:8080/`.

## Try the load-test script

With the app running locally in another terminal:

```bash
python scripts/load_test.py --url "http://127.0.0.1:8080/work?iterations=250000" --requests 100 --workers 10
```

Only run load tests against infrastructure you own or are authorized to test. Increase traffic gradually and keep an eye on your machine/cluster resources.

## Deploy to Kubernetes

Requirements: a working Kubernetes cluster, `kubectl`, and **Metrics Server** installed and reporting resource metrics. A local cluster such as minikube or kind is suitable for learning.

1. Build and publish the image, or let the GitHub Actions workflow do so after you configure the repository.
2. Edit `k8s/deployment.yaml` and replace `ghcr.io/REPLACE_WITH_GITHUB_USERNAME/autoscale-cloud-demo:latest` with your actual image name/tag.
3. Apply the manifests:

   ```bash
   kubectl apply -k k8s/
   ```

4. Check rollout and autoscaler status:

   ```bash
   kubectl rollout status deployment/autoscale-demo -n autoscale-demo
   kubectl get pods,svc,hpa -n autoscale-demo
   kubectl top pods -n autoscale-demo
   ```

5. In another terminal, port-forward the Service:

   ```bash
   kubectl port-forward service/autoscale-demo 8080:80 -n autoscale-demo
   ```

6. Run the load tester against `http://127.0.0.1:8080/work?iterations=250000` and watch replicas:

   ```bash
   kubectl get hpa,pods -n autoscale-demo -w
   ```

**Note:** HPA will not report CPU utilization or scale as expected unless Metrics Server is healthy and the cluster can schedule pods. Scaling is not instantaneous; allow time for metrics collection and stabilization.

## GitHub Actions / GHCR setup

The workflow at `.github/workflows/build-and-publish.yml` builds the Docker image and pushes it to GHCR on pushes to the default branch or manual runs. Repository Actions must be enabled, and the workflow needs package write permission. After the first run, update the Kubernetes image reference to the published image. If the package is private, configure cluster image-pull credentials or make the package public for a demo.

## Main project structure

```text
.
├── app.py
├── Dockerfile
├── docker-compose.yml
├── k8s/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   └── kustomization.yaml
├── scripts/load_test.py
├── docs/architecture.md
└── .github/workflows/build-and-publish.yml
```

## Next improvements

- Add Prometheus/Grafana dashboards and alerts.
- Add ingress and TLS for a real deployment.
- Add Infrastructure as Code (Terraform) for cloud resources.
- Add integration tests, image scanning, and a staging environment.
- Measure scaling behavior and document results with screenshots/graphs.

## Disclaimer

This is an educational starter project. Kubernetes manifests and publishing workflow must be configured for your cluster and GitHub account before deployment. Do not point a load test at production or third-party systems.
