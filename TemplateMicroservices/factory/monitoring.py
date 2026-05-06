import os

def create_monitoring_config(project_path):
    """Genera Prometheus y el DataSource de Grafana CORRECTO."""
    
    # Prometheus Config
    prom_content = """global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'api_microservice'
    static_configs:
      - targets: ['api:8000', 'host.docker.internal:8010']
"""
    with open(os.path.join(project_path, "prometheus.yml"), "w") as f:
        f.write(prom_content)

    # Grafana DataSource (FIXED)
    p = os.path.join(project_path, "provisioning", "datasources")
    os.makedirs(p, exist_ok=True)
    
    ds_content = """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
    jsonData:
      httpMethod: POST
      timeInterval: 15s
"""
    with open(os.path.join(p, "ds.yml"), "w") as f:
        f.write(ds_content)
