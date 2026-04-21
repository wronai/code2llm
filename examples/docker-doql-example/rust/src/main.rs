use std::env;
use std::collections::HashMap;
use serde::{Deserialize, Serialize};

#[derive(Serialize, Deserialize)]
struct Response {
    message: String,
    service: String,
    language: String,
    version: String,
    db_host: String,
}

#[tokio::main]
async fn main() {
    let port = env::var("PORT").unwrap_or_else(|_| "8080".to_string());
    let addr = format!("0.0.0.0:{}", port);
    
    let app = axum::Router::new()
        .route("/health", axum::routing::get(health_handler))
        .route("/api", axum::routing::get(api_handler));
    
    println!("Rust service listening on {}", addr);
    
    let listener = tokio::net::TcpListener::bind(&addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}

async fn health_handler() -> axum::Json<Response> {
    axum::Json(Response {
        message: "OK".to_string(),
        service: env::var("SERVICE_NAME").unwrap_or_else(|_| "rust-api".to_string()),
        language: "Rust".to_string(),
        version: "1.75".to_string(),
        db_host: env::var("DB_HOST").unwrap_or_else(|_| "database".to_string()),
    })
}

async fn api_handler() -> axum::Json<Response> {
    axum::Json(Response {
        message: "Hello from Rust service!".to_string(),
        service: env::var("SERVICE_NAME").unwrap_or_else(|_| "rust-api".to_string()),
        language: "Rust".to_string(),
        version: "1.75".to_string(),
        db_host: env::var("DB_HOST").unwrap_or_else(|_| "database".to_string()),
    })
}
