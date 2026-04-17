<template>
  <form class="form" @submit.prevent="submit">
    <h2>Приёмка товара</h2>

    <div class="field">
      <label>Поставщик</label>
      <input v-model="supplierName" type="text" placeholder='ООО "ДверьОпт"' required />
    </div>

    <h3>Позиции приёмки</h3>

    <div v-for="(item, i) in items" :key="i" class="row">
      <select v-model="item.si_product_id" required>
        <option value="" disabled>Выберите товар</option>
        <option v-for="p in products" :key="p.prod_id" :value="p.prod_id">
          {{ p.prod_name }} (ост. {{ p.prod_quantity }})
        </option>
      </select>
      <input v-model.number="item.si_quantity" type="number" min="1" placeholder="Кол-во" required />
      <button type="button" class="btn-remove" @click="items.splice(i, 1)">✕</button>
    </div>

    <button type="button" class="btn-add" @click="addItem">+ Добавить позицию</button>

    <div class="actions">
      <button type="submit" class="btn-submit" :disabled="loading">
        {{ loading ? "Оформляется..." : "Принять товар" }}
      </button>
    </div>

    <div v-if="result" class="result success">
      Приёмка #{{ result.shp_id }} от «{{ result.shp_supplier_name }}» завершена
    </div>
    <div v-if="error" class="result error">{{ error }}</div>
  </form>
</template>

<script>
import { getProducts, createShipment } from "../api/index.js";

export default {
  data() {
    return {
      supplierName: "",
      items: [{ si_product_id: "", si_quantity: 1 }],
      products: [],
      loading: false,
      result: null,
      error: null,
      resultHideTimer: null,
    };
  },
  async created() {
    const res = await getProducts();
    this.products = res.data;
  },
  beforeUnmount() {
    clearTimeout(this.resultHideTimer);
  },
  methods: {
    addItem() {
      this.items.push({ si_product_id: "", si_quantity: 1 });
    },
    scheduleResultHide() {
      clearTimeout(this.resultHideTimer);
      this.resultHideTimer = setTimeout(() => {
        this.result = null;
        this.resultHideTimer = null;
      }, 3000);
    },
    async submit() {
      this.loading = true;
      clearTimeout(this.resultHideTimer);
      this.resultHideTimer = null;
      this.result = null;
      this.error = null;
      try {
        const res = await createShipment({
          shp_supplier_name: this.supplierName,
          items: this.items,
        });
        this.result = res.data;
        this.scheduleResultHide();
        this.supplierName = "";
        this.items = [{ si_product_id: "", si_quantity: 1 }];
        const updated = await getProducts();
        this.products = updated.data;
      } catch (e) {
        this.error = e.response?.data?.detail || "Ошибка при приёмке товара";
      } finally {
        this.loading = false;
      }
    },
  },
};
</script>

<style scoped>
.form {
  background: #fff;
  border-radius: 12px;
  padding: 28px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

h2 {
  margin-bottom: 20px;
  font-size: 22px;
}

h3 {
  margin: 20px 0 12px;
  font-size: 16px;
  color: #555;
}

.field {
  margin-bottom: 14px;
}

.field label {
  display: block;
  margin-bottom: 4px;
  font-size: 14px;
  color: #555;
}

.field input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 15px;
}

.row {
  display: flex;
  gap: 10px;
  margin-bottom: 10px;
  align-items: center;
}

.row select {
  flex: 3;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.row input {
  flex: 1;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
}

.btn-remove {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 18px;
  cursor: pointer;
}

.btn-add {
  background: none;
  border: 1px dashed #16a34a;
  color: #16a34a;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 4px;
}

.actions {
  margin-top: 24px;
}

.btn-submit {
  background: #16a34a;
  color: #fff;
  border: none;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit:hover {
  background: #15803d;
}

.btn-submit:disabled {
  background: #86efac;
  cursor: not-allowed;
}

.result {
  margin-top: 16px;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 15px;
}

.success {
  background: #d1fae5;
  color: #065f46;
}

.error {
  background: #fee2e2;
  color: #991b1b;
}
</style>
