import axios from "axios";

const api = axios.create({
  baseURL: "/api",
});

export function getProducts() {
  return api.get("/products/");
}

export function createOrder(data) {
  return api.post("/orders/", data);
}

export function createShipment(data) {
  return api.post("/shipments/", data);
}
