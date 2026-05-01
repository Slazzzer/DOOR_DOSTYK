<template>
  <form class="form" @submit.prevent="submit">
    <h2>Приёмка товара</h2>

    <div class="field">
      <label>Поставщик</label>
      <input v-model="supplierName" type="text" placeholder='ООО "ДверьОпт"' required />
    </div>

    <h3>Позиции приёмки</h3>

    <div
      v-for="(item, i) in items"
      :key="item._uid"
      class="row"
      :class="{ 'row-picker-open': pickerOpenIndex === i }"
    >
      <div class="product-picker">
        <input
          v-model="item.search"
          type="search"
          class="picker-input"
          placeholder="Начните вводить название товара"
          autocomplete="off"
          @focus="openPicker(i)"
          @input="onSearchInput(i)"
        />
        <ul v-show="pickerOpenIndex === i" class="picker-list" role="listbox">
          <li v-if="!filteredProducts(item).length" class="picker-empty">
            Нет товаров по запросу
          </li>
          <template v-else>
            <li
              v-for="p in filteredProducts(item)"
              :key="p.prod_id"
              role="option"
              class="picker-option"
              :class="{ selected: item.si_product_id === p.prod_id }"
              @mousedown.prevent="selectProduct(i, p)"
            >
              {{ p.prod_name }} (ост. {{ p.prod_quantity }})
            </li>
          </template>
        </ul>
      </div>
      <input
        v-model.number="item.si_quantity"
        type="number"
        min="1"
        class="qty-input"
        placeholder="Кол-во"
        required
      />
      <div class="cell stock-cell">
        <span class="cell-label">станет</span>
        <span class="cell-value">{{ projectedStockLabel(item) }}</span>
      </div>
      <button
        type="button"
        class="btn-remove"
        @click="removeRow(i)"
        aria-label="Удалить позицию"
      >
        ✕
      </button>
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

let _rowSeq = 0;
function makeItem() {
  return { _uid: ++_rowSeq, si_product_id: "", si_quantity: 1, search: "" };
}

export default {
  data() {
    return {
      supplierName: "",
      pickerOpenIndex: null,
      items: [makeItem()],
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
  },
  methods: {
    async fetchProducts() {
      const res = await getProducts();
      this.products = res.data;
    },
    productOf(item) {
      if (item.si_product_id === "" || item.si_product_id == null) return null;
      return this.products.find((p) => p.prod_id === item.si_product_id) || null;
    },
    filteredProducts(item) {
      const term = (item.search || "").trim().toLowerCase();
      if (!term) return this.products;
      return this.products.filter((p) =>
        p.prod_name.toLowerCase().includes(term)
      );
    },
    openPicker(i) {
      this.pickerOpenIndex = i;
    },
    onSearchInput(i) {
      this.pickerOpenIndex = i;
      this.items[i].si_product_id = "";
    },
    selectProduct(i, p) {
      const it = this.items[i];
      it.si_product_id = p.prod_id;
      it.search = p.prod_name;
      this.pickerOpenIndex = null;
    },
    addItem() {
      this.items.push(makeItem());
    },
    removeRow(i) {
      this.pickerOpenIndex = null;
      this.items.splice(i, 1);
      if (!this.items.length) this.items.push(makeItem());
    },
    quantityOf(item) {
      const q = Number(item.si_quantity);
      return Number.isFinite(q) && q > 0 ? q : 0;
    },
    projectedStock(item) {
      const p = this.productOf(item);
      if (!p) return null;
      return p.prod_quantity + this.quantityOf(item);
    },
    projectedStockLabel(item) {
      const v = this.projectedStock(item);
      return v == null ? "—" : v;
    },
    formatSubmitError(detail) {
      if (detail == null) return "Ошибка при приёмке товара";
      if (typeof detail === "string") return detail;
      if (Array.isArray(detail)) {
        const parts = detail
          .map((x) => (typeof x === "object" && x?.msg ? x.msg : String(x)))
          .filter(Boolean);
        return parts.length ? parts.join(" ") : "Ошибка при приёмке товара";
      }
      return "Ошибка при приёмке товара";
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
    async submit() {
      for (const it of this.items) {
        if (it.si_product_id === "" || it.si_product_id == null) {
          this.error = "Выберите товар в каждой позиции приёмки";
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
        const payload = {
          shp_supplier_name: this.supplierName,
          items: this.items.map((it) => ({
            si_product_id: it.si_product_id,
            si_quantity: it.si_quantity,
          })),
        };
        const res = await createShipment(payload);
        this.result = res.data;
        this.scheduleResultHide();
        this.supplierName = "";
        this.items = [makeItem()];
        await this.fetchProducts();
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
  align-items: center;
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

.picker-input {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  background: #fff;
  color: #1a1a2e;
}

.picker-input:focus {
  outline: none;
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
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
  border: 1px solid #bbf7d0;
  border-radius: 8px;
  box-shadow: 0 10px 30px rgba(22, 163, 74, 0.15);
  z-index: 30;
}

.picker-option {
  padding: 8px 12px;
  font-size: 14px;
  cursor: pointer;
}

.picker-option:hover {
  background: #f0fdf4;
}

.picker-option.selected {
  background: #dcfce7;
}

.picker-empty {
  padding: 10px 12px;
  font-size: 14px;
  color: #6b7280;
}

.qty-input {
  flex: 0 0 90px;
  padding: 10px 12px;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
}

.cell {
  flex: 0 0 auto;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  line-height: 1.15;
  white-space: nowrap;
}

.cell-label {
  font-size: 11px;
  color: #6b7280;
  text-transform: lowercase;
}

.cell-value {
  font-size: 14px;
  color: #1a1a2e;
  font-variant-numeric: tabular-nums;
  font-weight: 600;
}

.stock-cell {
  min-width: 80px;
}

.stock-cell .cell-value {
  color: #15803d;
}

.btn-remove {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 6px;
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
