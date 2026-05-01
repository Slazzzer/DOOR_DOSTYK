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
              :class="{ selected: item.oi_product_id === p.prod_id }"
              @mousedown.prevent="selectProduct(i, p)"
            >
              {{ p.prod_name }} - {{ p.prod_price }} руб. (ост. {{ p.prod_quantity }})
            </li>
          </template>
        </ul>
      </div>
      <input
        v-model.number="item.oi_quantity"
        type="number"
        min="1"
        class="qty-input"
        placeholder="Кол-во"
        required
      />
      <div class="cell stock-cell" :class="{ negative: isOverstock(item) }">
        <span class="cell-label">ост.</span>
        <span class="cell-value">{{ remainingStockLabel(item) }}</span>
      </div>
      <div class="cell total-cell">
        <span class="cell-label">сумма</span>
        <span class="cell-value">{{ lineTotalLabel(item) }} руб.</span>
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

    <div class="grand-total">
      <span>Итого:</span>
      <strong>{{ grandTotalLabel }} руб.</strong>
    </div>

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

let _rowSeq = 0;
function makeItem() {
  return { _uid: ++_rowSeq, oi_product_id: "", oi_quantity: 1, search: "" };
}

const moneyFormatter = new Intl.NumberFormat("ru-RU", {
  minimumFractionDigits: 0,
  maximumFractionDigits: 2,
});

export default {
  data() {
    return {
      clientName: "",
      clientPhone: "",
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
  computed: {
    grandTotal() {
      return this.items.reduce((sum, it) => sum + this.lineTotal(it), 0);
    },
    grandTotalLabel() {
      return moneyFormatter.format(this.grandTotal);
    },
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
      if (item.oi_product_id === "" || item.oi_product_id == null) return null;
      return this.products.find((p) => p.prod_id === item.oi_product_id) || null;
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
      // любое ручное изменение текста сбрасывает выбранный товар:
      // подпись и реально выбранный prod_id не должны расходиться
      this.pickerOpenIndex = i;
      this.items[i].oi_product_id = "";
    },
    selectProduct(i, p) {
      const it = this.items[i];
      it.oi_product_id = p.prod_id;
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
      const q = Number(item.oi_quantity);
      return Number.isFinite(q) && q > 0 ? q : 0;
    },
    remainingStock(item) {
      const p = this.productOf(item);
      if (!p) return null;
      return p.prod_quantity - this.quantityOf(item);
    },
    remainingStockLabel(item) {
      const v = this.remainingStock(item);
      return v == null ? "—" : v;
    },
    isOverstock(item) {
      const v = this.remainingStock(item);
      return v != null && v < 0;
    },
    lineTotal(item) {
      const p = this.productOf(item);
      if (!p) return 0;
      return Number(p.prod_price) * this.quantityOf(item);
    },
    lineTotalLabel(item) {
      return moneyFormatter.format(this.lineTotal(item));
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
        const payload = {
          ord_client_name: this.clientName.trim(),
          ord_client_phone: this.clientPhone.trim() || null,
          items: this.items.map((it) => ({
            oi_product_id: it.oi_product_id,
            oi_quantity: it.oi_quantity,
          })),
        };
        const res = await createOrder(payload);
        this.result = res.data;
        this.scheduleResultHide();
        this.clientName = "";
        this.clientPhone = "";
        this.items = [makeItem()];
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
  border-color: #3b82f6;
  box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.2);
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
}

.stock-cell {
  min-width: 64px;
}

.stock-cell.negative .cell-value {
  color: #dc2626;
  font-weight: 600;
}

.total-cell {
  min-width: 110px;
}

.total-cell .cell-value {
  font-weight: 600;
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
  border: 1px dashed #3b82f6;
  color: #3b82f6;
  padding: 8px 16px;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  margin-top: 4px;
}

.grand-total {
  margin-top: 20px;
  padding: 12px 16px;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 16px;
}

.grand-total strong {
  font-size: 18px;
  font-variant-numeric: tabular-nums;
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
