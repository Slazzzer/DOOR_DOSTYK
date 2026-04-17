<template>
  <form class="form" @submit.prevent="submit">
    <h2>Новый заказ</h2>

    <div class="field">
      <label>ФИО клиента</label>
      <input v-model="clientName" type="text" placeholder="Иванов Сергей Петрович" required />
    </div>

    <div class="field">
      <label>Телефон (необязательно)</label>
      <input
        v-model="clientPhone"
        type="tel"
        inputmode="tel"
        autocomplete="tel"
        placeholder="+79205386674"
      />
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

    <div
      v-for="(item, i) in items"
      :key="i"
      class="row"
      :class="{ 'row-picker-open': pickerOpenIndex === i }"
    >
      <div class="product-picker">
        <button type="button" class="picker-trigger" @click="togglePicker(i)">
          {{ pickerLabel(item) }}
        </button>
        <ul v-show="pickerOpenIndex === i" class="picker-list" role="listbox">
          <li v-if="!products.length" class="picker-empty">Нет товаров по запросу</li>
          <template v-else>
            <li
              v-for="p in products"
              :key="p.prod_id"
              role="option"
              class="picker-option"
              :class="{ selected: item.oi_product_id === p.prod_id }"
              @mousedown.prevent="selectProduct(i, p.prod_id)"
            >
              {{ p.prod_name }} - {{ p.prod_price }} руб. (ост. {{ p.prod_quantity }})
            </li>
          </template>
        </ul>
      </div>
      <input v-model.number="item.oi_quantity" type="number" min="1" placeholder="Кол-во" required />
      <button type="button" class="btn-remove" @click="removeRow(i)">✕</button>
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
      pickerOpenIndex: null,
      items: [{ oi_product_id: "", oi_quantity: 1 }],
      products: [],
      loading: false,
      result: null,
      error: null,
      resultHideTimer: null,
      errorHideTimer: null,
    };
  },
  async created() {
    await this.fetchProducts();
  },
  mounted() {
    this._pickerDocClose = (e) => {
      if (this.pickerOpenIndex === null) return;
      const el = this.$el;
      if (!el) return;
      for (const p of el.querySelectorAll(".product-picker")) {
        if (p.contains(e.target)) return;
      }
      this.pickerOpenIndex = null;
    };
    document.addEventListener("mousedown", this._pickerDocClose);
  },
  beforeUnmount() {
    document.removeEventListener("mousedown", this._pickerDocClose);
    clearTimeout(this.resultHideTimer);
    clearTimeout(this.errorHideTimer);
    clearTimeout(this.searchDebounce);
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
    removeRow(i) {
      this.pickerOpenIndex = null;
      this.items.splice(i, 1);
    },
    togglePicker(i) {
      this.pickerOpenIndex = this.pickerOpenIndex === i ? null : i;
    },
    selectProduct(rowIndex, prodId) {
      this.items[rowIndex].oi_product_id = prodId;
      this.pickerOpenIndex = null;
    },
    pickerLabel(item) {
      const id = item.oi_product_id;
      if (id === "" || id == null) return "Выберите товар";
      const p = this.products.find((x) => x.prod_id === id);
      return p
        ? `${p.prod_name} - ${p.prod_price} руб. (ост. ${p.prod_quantity})`
        : `Товар #${id}`;
    },
    scheduleResultHide() {
      clearTimeout(this.resultHideTimer);
      this.resultHideTimer = setTimeout(() => {
        this.result = null;
        this.resultHideTimer = null;
      }, 3000);
    },
    scheduleErrorHide() {
      clearTimeout(this.errorHideTimer);
      this.errorHideTimer = setTimeout(() => {
        this.error = null;
        this.errorHideTimer = null;
      }, 3000);
    },
    formatSubmitError(detail) {
      if (detail == null) return "Ошибка при оформлении заказа";
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        const parts = detail
          .map((x) => (typeof x === "object" && x?.msg ? x.msg : String(x)))
          .filter(Boolean);
        return parts.length ? parts.join(" ") : "Ошибка при оформлении заказа";
      }
      return "Ошибка при оформлении заказа";
    },
    async submit() {
      for (const it of this.items) {
        if (it.oi_product_id === "" || it.oi_product_id == null) {
          this.error = "Выберите товар в каждой позиции заказа";
          this.scheduleErrorHide();
          return;
        }
      }
      this.loading = true;
      clearTimeout(this.resultHideTimer);
      clearTimeout(this.errorHideTimer);
      this.resultHideTimer = null;
      this.errorHideTimer = null;
      this.result = null;
      this.error = null;
      try {
        const res = await createOrder({
          ord_client_name: this.clientName.trim(),
          ord_client_phone: this.clientPhone.trim() || null,
          items: this.items,
        });
        this.result = res.data;
        this.scheduleResultHide();
        this.clientName = "";
        this.clientPhone = "";
        this.items = [{ oi_product_id: "", oi_quantity: 1 }];
        await this.fetchProducts();
        this.$emit("orders-changed");
      } catch (e) {
        this.error = this.formatSubmitError(e.response?.data?.detail);
        this.scheduleErrorHide();
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
  align-items: flex-start;
  position: relative;
}

.row-picker-open {
  z-index: 25;
}

.product-picker {
  position: relative;
  flex: 3;
  min-width: 0;
}

.picker-trigger {
  width: 100%;
  text-align: left;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  cursor: pointer;
  color: #1a1a2e;
}

.picker-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: min(40vh, 240px);
  overflow-y: auto;
  margin: 0;
  padding: 4px 0;
  list-style: none;
  background: #fff;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.12);
  z-index: 30;
}

.picker-option {
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
}

.picker-option:hover {
  background: #f3f4f6;
}

.picker-option.selected {
  background: #e0ecff;
}

.picker-empty {
  padding: 10px 12px;
  font-size: 14px;
  color: #6b7280;
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
