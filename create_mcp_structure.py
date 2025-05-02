import os

def create_if_not_exists(path, is_file=False, content=""):
    """Create a directory or file only if it doesn't exist"""
    # Check if the path exists
    if os.path.exists(path):
        return False  # Path already exists, no action taken
    
    # Create directory if needed
    if not is_file:
        os.makedirs(path, exist_ok=True)
        return True  # Directory created
    else:
        # Create parent directories if they don't exist
        directory = os.path.dirname(path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        # Create the file
        with open(path, 'w') as file:
            file.write(content)
        return True  # File created

def create_fastapi_mcp_structure():
    """Create the FastAPI MCP project structure, only adding missing elements"""
    base_dir = "mcp-ecommerce"
    changes_made = 0
    
    # Create root directory if needed
    if create_if_not_exists(base_dir):
        print(f"Created directory: {base_dir}")
        changes_made += 1
    
    # Services to create
    services = [
        "api-gateway",
        "model-registry",
        "orchestration-service",
        "model-runner",
        "data-access",
        "monitoring-service"
    ]
    
    # Common FastAPI files and directories for each service
    common_files = [
        "Dockerfile",
        "requirements.txt",
        "main.py",
        "app/__init__.py",
        "app/core/__init__.py",
        "app/core/config.py",
        "app/core/events.py",
        "app/api/__init__.py",
        "app/api/router.py",
        "app/api/dependencies.py",
        "app/api/endpoints/__init__.py",
        "app/schemas/__init__.py",
        "tests/__init__.py",
        "tests/conftest.py"
    ]
    
    # Create services
    for service in services:
        service_path = os.path.join(base_dir, "services", service)
        if create_if_not_exists(service_path):
            print(f"Created directory: {service_path}")
            changes_made += 1
        
        # Create common FastAPI files
        for file_path in common_files:
            full_path = os.path.join(service_path, file_path)
            if create_if_not_exists(full_path, is_file=True):
                print(f"Created file: {full_path}")
                changes_made += 1
        
        # Create service-specific files
        specific_files = []
        if service == "api-gateway":
            specific_files = get_api_gateway_files()
        elif service == "model-registry":
            specific_files = get_model_registry_files()
        elif service == "orchestration-service":
            specific_files = get_orchestration_files()
        elif service == "model-runner":
            specific_files = get_model_runner_files()
        elif service == "data-access":
            specific_files = get_data_access_files()
        elif service == "monitoring-service":
            specific_files = get_monitoring_files()
        
        for file_path in specific_files:
            full_path = os.path.join(service_path, file_path)
            if create_if_not_exists(full_path, is_file=True):
                print(f"Created file: {full_path}")
                changes_made += 1
    
    # Create supporting directories
    support_dirs = [
        "api-specs",
        "dashboards/business-dashboards",
        "dashboards/model-dashboards",
        "dashboards/system-dashboards",
        "data-policies",
        "models/sample",
        "policies",
        "schemas",
        "scripts",
        "threat-models",
        "docs/api",
        "docs/architecture",
        "docs/guides",
        "docs/tutorials"
    ]
    
    for directory in support_dirs:
        dir_path = os.path.join(base_dir, directory)
        if create_if_not_exists(dir_path):
            print(f"Created directory: {dir_path}")
            changes_made += 1
        
        # Add .gitkeep file
        gitkeep_path = os.path.join(dir_path, ".gitkeep")
        if create_if_not_exists(gitkeep_path, is_file=True):
            print(f"Created file: {gitkeep_path}")
            changes_made += 1
    
    # Create README if it doesn't exist
    readme_path = os.path.join(base_dir, "README.md")
    readme_content = """# Model Control Protocol (MCP) for E-commerce

A comprehensive architecture for managing AI models in e-commerce applications.

## Overview

This project implements a Model Control Protocol (MCP) system for e-commerce platforms, providing:

- Secure model management and versioning
- Request orchestration and traffic management
- Model execution and scaling
- Data access with governance and privacy controls
- Comprehensive monitoring and logging

## Getting Started

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run each service: `cd services/api-gateway && uvicorn main:app --reload`

## Documentation

See the `/docs` directory for detailed documentation on the architecture and usage.
"""
    if create_if_not_exists(readme_path, is_file=True, content=readme_content):
        print(f"Created file: {readme_path}")
        changes_made += 1
    
    return changes_made

def get_api_gateway_files():
    """Get API Gateway specific files"""
    return [
        "app/api/endpoints/model_routes.py",
        "app/api/endpoints/admin_routes.py",
        "app/auth/__init__.py",
        "app/auth/jwt_handler.py",
        "app/auth/security.py",
        "app/middleware/__init__.py",
        "app/middleware/logging.py",
        "app/middleware/rate_limiter.py",
        "app/models/__init__.py",
        "app/models/token.py",
        "app/models/request_models.py",
        "app/schemas/model.py",
        "app/schemas/user.py",
        "app/utils/__init__.py",
        "app/utils/request_formatter.py",
        "tests/api/test_model_routes.py",
        "tests/api/test_admin_routes.py",
        "tests/auth/test_jwt.py"
    ]

def get_model_registry_files():
    """Get Model Registry specific files"""
    return [
        "app/api/endpoints/registry_routes.py",
        "app/api/endpoints/version_routes.py",
        "app/db/__init__.py",
        "app/db/base.py",
        "app/db/session.py",
        "app/db/repositories/__init__.py",
        "app/db/repositories/model_repository.py",
        "app/db/repositories/version_repository.py",
        "app/models/__init__.py",
        "app/models/model.py",
        "app/models/version.py",
        "app/models/metadata.py",
        "app/schemas/model.py",
        "app/schemas/version.py",
        "app/services/__init__.py",
        "app/services/model_service.py",
        "app/services/version_service.py",
        "app/services/validation_service.py",
        "app/storage/__init__.py",
        "app/storage/model_storage.py",
        "app/storage/storage_provider.py",
        "alembic/__init__.py",
        "alembic/versions/.gitkeep",
        "alembic/alembic.ini",
        "tests/api/test_registry_routes.py",
        "tests/api/test_version_routes.py",
        "tests/services/test_model_service.py"
    ]

def get_orchestration_files():
    """Get Orchestration Service specific files"""
    return [
        "app/api/endpoints/orchestrator_routes.py",
        "app/api/endpoints/admin_routes.py",
        "app/dispatcher/__init__.py",
        "app/dispatcher/router.py",
        "app/dispatcher/traffic_manager.py",
        "app/dispatcher/batch_processor.py",
        "app/policies/__init__.py",
        "app/policies/policy_engine.py",
        "app/policies/rules.py",
        "app/policies/conditions.py",
        "app/fallback/__init__.py",
        "app/fallback/fallback_manager.py",
        "app/fallback/circuit_breaker.py",
        "app/fallback/static_responses.py",
        "app/clients/__init__.py",
        "app/clients/registry_client.py",
        "app/clients/model_client.py",
        "app/schemas/request.py",
        "app/schemas/response.py",
        "tests/dispatcher/test_router.py",
        "tests/dispatcher/test_traffic_manager.py",
        "tests/policies/test_policy_engine.py"
    ]

def get_model_runner_files():
    """Get Model Runner specific files"""
    return [
        "app/api/endpoints/inference_routes.py",
        "app/api/endpoints/admin_routes.py",
        "app/loader/__init__.py",
        "app/loader/model_loader.py",
        "app/loader/version_manager.py",
        "app/loader/registry_client.py",
        "app/execution/__init__.py",
        "app/execution/executor.py",
        "app/execution/batch_executor.py",
        "app/execution/context_manager.py",
        "app/transformation/__init__.py",
        "app/transformation/input_transformer.py",
        "app/transformation/output_transformer.py",
        "app/scaling/__init__.py",
        "app/scaling/resource_monitor.py",
        "app/scaling/autoscaler.py",
        "app/scaling/queue_manager.py",
        "app/runtime/__init__.py",
        "app/runtime/tensorflow_runtime.py",
        "app/runtime/pytorch_runtime.py",
        "app/runtime/onnx_runtime.py",
        "app/schemas/inference.py",
        "app/schemas/model.py",
        "tests/loader/test_model_loader.py",
        "tests/execution/test_executor.py"
    ]

def get_data_access_files():
    """Get Data Access specific files"""
    return [
        "app/api/endpoints/data_routes.py",
        "app/api/endpoints/admin_routes.py",
        "app/connectors/__init__.py",
        "app/connectors/database_connector.py",
        "app/connectors/product_catalog.py",
        "app/connectors/customer_data.py",
        "app/connectors/order_system.py",
        "app/connectors/analytics_store.py",
        "app/transformers/__init__.py",
        "app/transformers/product_transformer.py",
        "app/transformers/customer_transformer.py",
        "app/transformers/order_transformer.py",
        "app/cache/__init__.py",
        "app/cache/cache_manager.py",
        "app/cache/product_cache.py",
        "app/cache/customer_cache.py",
        "app/governance/__init__.py",
        "app/governance/policy_enforcer.py",
        "app/governance/pii_handler.py",
        "app/governance/compliance.py",
        "app/schemas/product.py",
        "app/schemas/customer.py",
        "app/schemas/order.py",
        "tests/connectors/test_product_catalog.py",
        "tests/governance/test_pii_handler.py"
    ]

def get_monitoring_files():
    """Get Monitoring Service specific files"""
    return [
        "app/api/endpoints/metrics_routes.py",
        "app/api/endpoints/admin_routes.py",
        "app/collectors/__init__.py",
        "app/collectors/metrics_collector.py",
        "app/collectors/model_metrics.py",
        "app/collectors/system_metrics.py",
        "app/collectors/business_metrics.py",
        "app/loggers/__init__.py",
        "app/loggers/request_logger.py",
        "app/loggers/error_logger.py",
        "app/loggers/audit_logger.py",
        "app/alerting/__init__.py",
        "app/alerting/alert_manager.py",
        "app/alerting/notification_service.py",
        "app/alerting/alert_rules.py",
        "app/visualization/__init__.py",
        "app/visualization/dashboard_generator.py",
        "app/visualization/report_generator.py",
        "app/visualization/chart_generator.py",
        "app/schemas/metrics.py",
        "app/schemas/alerts.py",
        "tests/collectors/test_model_metrics.py",
        "tests/alerting/test_alert_manager.py"
    ]

if __name__ == "__main__":
    changes = create_fastapi_mcp_structure()
    print(f"\nMCP structure setup complete! {changes} new files/directories created.")
    if changes == 0:
        print("No changes were needed - all files and directories already exist.")
    else:
        print("Only missing components were created, existing files were preserved.")
    print("You can find the complete structure in the 'mcp-ecommerce' directory.")