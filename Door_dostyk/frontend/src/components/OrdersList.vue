<template>
  <section class="orders-list">
    <div class="head">
      <h2>Журнал заказов</h2>
      <button type="button" class="btn-refresh" @click="load">Обновить</button>
    </div>
    <p v-if="loading" class="muted">Загрузка</p>
    <p v-else-if="!orders.length" class="muted">Заказов пока нет.</p>
    <div v-else class="cards">
      <article v-for="o in orders" :key="o.ord_id" class="card">
        <header>
          <strong>Заказ #{{ o.ord_id }}</strong>
          <span class="badge">{{ o.ord_status }}</span>
        </header>
        <p class="meta">
          {{ o.ord_client_name }}
          <span v-if="o.ord_client_phone">, {{ o.ord_client_phone }}</span>
        </p>
        <p class="sum">{{ o.ord_total_amount }} руб.</p>
        <p class="date">{{ formatDate(o.ord_created_at) }}</p>
        <ul v-if="o.items?.length" class="lines">
          <li v-for="it in o.items" :key="it.oi_id">
            Товар #{{ it.oi_product_id }}, кол-во {{ it.oi_quantity }}, цена {{ it.oi_price }} руб.
          </li>
        </ul>
      </article>
    </div>
    <div v-if="error" class="error">{{ error }}</div>
  </section>
</template>

<script>
import { getOrders } from "../api/index.js";

export default {
  data() {
    return {
      orders: [],
      loading: false,
      error: null,
    };
  },
  created() {
    this.load();
  },
  methods: {
    async load() {
      this.loading = true;
      this.error = null;
      try {
        const res = await getOrders();
        this.orders = res.data;
      } catch (e) {
        this.error = e.response?.data?.detail || "Не удалось загрузить заказы";
      } finally {
        this.loading = false;
      }
    },
    formatDate(iso) {
      if (!iso) return "";
      try {
        return new Date(iso).toLocaleString("ru-RU");
      } catch {
        return String(iso);
      }
    },
  },
};
</script>

<style scoped>
.orders-list {
  margin-top: 32px;
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.head h2 {
  font-size: 22px;
}

.btn-refresh {
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  padding: 8px 14px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
}

.btn-refresh:hover {
  background: #e5e7eb;
}

.muted {
  color: #6b7280;
  font-size: 15px;
}

.cards {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.card {
  border: 1px solid #e5e7eb;
  border-radius: 10px;
  padding: 14px 16px;
}

.card header {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 6px;
}

.badge {
  font-size: 12px;
  text-transform: uppercase;
  background: #dbeafe;
  color: #1e40af;
  padding: 2px 8px;
  border-radius: 6px;
}

.meta {
  font-size: 14px;
  color: #4b5563;
}

.sum {
  font-weight: 600;
  margin-top: 6px;
}

.date {
  font-size: 13px;
  color: #9ca3af;
  margin-top: 4px;
}

.lines {
  margin-top: 10px;
  padding-left: 18px;
  font-size: 13px;
  color: #374151;
}

.error {
  margin-top: 12px;
  padding: 12px;
  background: #fee2e2;
  color: #991b1b;
  border-radius: 8px;
}
</style>
