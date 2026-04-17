import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

export function getProducts(params = {}) {
  return api.get("/products/", { params });
}

export function getOrders() {
  return api.get("/orders/");
}

export function createOrder(data) {
  return api.post("/orders/", data);
}

export function createShipment(data) {
  return api.post("/shipments/", data);
}
