<template>
  <form class="form" @submit.prevent="submit">
    <h2>Новый заказ</h2>

    <div class="field">
      <label>ФИО клиента</label>
      <input v-model="clientName" type="text" placeholder="Иванов Сергей Петрович" required />
    </div>

    <div class="field">
      <label>Телефон</label>
      <input v-model="clientPhone" type="text" placeholder="+7-900-123-45-67" />
    </div>

    <h3>Позиции заказа</h3>

    <div class="field">
      <label>Поиск товара в каталоге</label>
      <input
        v-model="productSearch"
        type="search"
        placeholder="Начните вводить название"
        autocomplete="off"
        @input="onSearchInput"
      />
    </div>

    <div v-for="(item, i) in items" :key="i" class="row">
      <select v-model="item.oi_product_id" required>
        <option value="" disabled>Выберите товар</option>
        <option v-for="p in products" :key="p.prod_id" :value="p.prod_id">
          {{ p.prod_name }} - {{ p.prod_price }} руб. (ост. {{ p.prod_quantity }})
        </option>
      </select>
      <input v-model.number="item.oi_quantity" type="number" min="1" placeholder="Кол-во" required />
      <button type="button" class="btn-remove" @click="items.splice(i, 1)">✕</button>
    </div>

    <button type="button" class="btn-add" @click="addItem">+ Добавить позицию</button>

    <div class="actions">
      <button type="submit" class="btn-submit" :disabled="loading">
        {{ loading ? "Оформляется..." : "Оформить заказ" }}
      </button>
    </div>

    <div v-if="result" class="result success">
      Заказ #{{ result.ord_id }} оформлен на сумму {{ result.ord_total_amount }} руб.
    </div>
    <div v-if="error" class="result error">{{ error }}</div>
  </form>
</template>

<script>
import { getProducts, createOrder } from "../api/index.js";

export default {
  data() {
    return {
      clientName: "",
      clientPhone: "",
      productSearch: "",
      searchDebounce: null,
      items: [{ oi_product_id: "", oi_quantity: 1 }],
      products: [],
      loading: false,
      result: null,
      error: null,
    };
  },
  async created() {
    await this.fetchProducts();
  },
  methods: {
    onSearchInput() {
      clearTimeout(this.searchDebounce);
      this.searchDebounce = setTimeout(() => this.fetchProducts(), 320);
    },
    async fetchProducts() {
      const res = await getProducts({
        search: this.productSearch.trim() || undefined,
      });
      this.products = res.data;
    },
    addItem() {
      this.items.push({ oi_product_id: "", oi_quantity: 1 });
    },
    async submit() {
      this.loading = true;
      this.result = null;
      this.error = null;
      try {
        const res = await createOrder({
          ord_client_name: this.clientName,
          ord_client_phone: this.clientPhone || null,
          items: this.items,
        });
        this.result = res.data;
        this.clientName = "";
        this.clientPhone = "";
        this.items = [{ oi_product_id: "", oi_quantity: 1 }];
        await this.fetchProducts();
      } catch (e) {
        this.error = e.response?.data?.detail || "Ошибка при оформлении заказа";
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
  border: 1px dashed #3b82f6;
  color: #3b82f6;
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
  background: #3b82f6;
  color: #fff;
  border: none;
  padding: 12px 28px;
  border-radius: 8px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-submit:hover {
  background: #2563eb;
}

.btn-submit:disabled {
  background: #93c5fd;
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
