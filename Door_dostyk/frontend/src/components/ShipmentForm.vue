<template>
  <form class="form" @submit.prevent="submit">
    <h2>Приёмка товара</h2>

    <div class="field">
      <label>Поставщик</label>
      <input v-model="supplierName" type="text" placeholder='ООО "ДверьОпт"' required />
    </div>

    <h3>Позиции приёмки</h3>

    <div class="field">
      <label>Поиск товара</label>
      <input
        v-model="productSearch"
        type="search"
        placeholder="Начните вводить название"
        autocomplete="off"
      />
    </div>

    <div
      v-for="(item, i) in items"
      :key="i"
      class="row"
      :class="{ 'row-open': pickerOpenIndex === i }"
    >
      <div class="combo">
        <div class="combo-picker">
          <button type="button" class="combo-trigger" @click="togglePicker(i)">
            {{ pickerLabel(item) }}
          </button>
          <ul v-show="pickerOpenIndex === i" class="picker-list">
            <li v-if="!filteredList.length" class="picker-empty">Нет товаров по запросу</li>
            <li
              v-for="p in filteredList"
              :key="p.prod_id"
              class="picker-option"
              :class="{ selected: item.si_product_id === p.prod_id }"
              @mousedown.prevent="selectProduct(i, p.prod_id)"
            >
              {{ p.prod_name }} (ост. {{ p.prod_quantity }})
            </li>
          </ul>
        </div>
        <input
          v-model.number="item.si_quantity"
          type="number"
          min="1"
          class="combo-qty"
          placeholder="Кол-во"
          required
        />
      </div>
      <button type="button" class="btn-remove" @click="removeRow(i)">✕</button>
    </div>

    <button type="button" class="btn-add" @click="addItem">+ Добавить позицию</button>

    <div class="actions">
      <button type="submit" class="btn-submit" :disabled="loading">
        {{ loading ? "Оформляется..." : "Принять товар" }}
      </button>
      <div v-if="shipmentTotal > 0" class="total-badge">
        Стоимость поставки: {{ shipmentTotalLabel }} руб.
        &nbsp;·&nbsp;
        На складе станет: {{ projectedTotalStock }} шт.
      </div>
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
      productSearch: "",
      pickerOpenIndex: null,
      items: [{ si_product_id: "", si_quantity: 1 }],
      products: [],
      loading: false,
      result: null,
      error: null,
      resultHideTimer: null,
      errorHideTimer: null,
    };
  },
  computed: {
    filteredList() {
      const term = this.productSearch.trim().toLowerCase();
      if (!term) return this.products;
      return this.products.filter((p) =>
        p.prod_name.toLowerCase().includes(term)
      );
    },
    shipmentTotal() {
      return this.items.reduce((sum, it) => {
        const p = this.products.find((x) => x.prod_id === it.si_product_id);
        if (!p) return sum;
        const qty = Number(it.si_quantity);
        return sum + (Number.isFinite(qty) && qty > 0 ? Number(p.prod_price) * qty : 0);
      }, 0);
    },
    shipmentTotalLabel() {
      return new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 }).format(
        this.shipmentTotal
      );
    },
    projectedTotalStock() {
      const currentTotal = this.products.reduce(
        (s, p) => s + Number(p.prod_quantity || 0),
        0
      );
      const addedTotal = this.items.reduce((s, it) => {
        if (!it.si_product_id) return s;
        const qty = Number(it.si_quantity);
        return s + (Number.isFinite(qty) && qty > 0 ? qty : 0);
      }, 0);
      return currentTotal + addedTotal;
    },
  },
  async created() {
    const res = await getProducts();
    this.products = res.data;
  },
  mounted() {
    this._docClose = (e) => {
      if (this.pickerOpenIndex === null) return;
      const root = this.$el;
      if (!root) return;
      for (const el of root.querySelectorAll(".combo-picker")) {
        if (el.contains(e.target)) return;
      }
      this.pickerOpenIndex = null;
    };
    document.addEventListener("mousedown", this._docClose);
  },
  beforeUnmount() {
    document.removeEventListener("mousedown", this._docClose);
    clearTimeout(this.resultHideTimer);
    clearTimeout(this.errorHideTimer);
  },
  methods: {
    togglePicker(i) {
      this.pickerOpenIndex = this.pickerOpenIndex === i ? null : i;
    },
    selectProduct(i, prodId) {
      this.items[i].si_product_id = prodId;
      this.pickerOpenIndex = null;
    },
    pickerLabel(item) {
      const p = this.products.find((x) => x.prod_id === item.si_product_id);
      return p ? `${p.prod_name} (ост. ${p.prod_quantity})` : "Выберите товар";
    },
    addItem() {
      this.items.push({ si_product_id: "", si_quantity: 1 });
    },
    removeRow(i) {
      this.pickerOpenIndex = null;
      this.items.splice(i, 1);
      if (!this.items.length) this.items.push({ si_product_id: "", si_quantity: 1 });
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
      this.resultHideTimer = setTimeout(() => (this.result = null), 3000);
    },
    scheduleErrorHide() {
      clearTimeout(this.errorHideTimer);
      this.errorHideTimer = setTimeout(() => (this.error = null), 3000);
    },
    async submit() {
      for (const it of this.items) {
        if (!it.si_product_id) {
          this.error = "Выберите товар в каждой позиции приёмки";
          this.scheduleErrorHide();
          return;
        }
      }
      this.loading = true;
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
        this.productSearch = "";
        this.items = [{ si_product_id: "", si_quantity: 1 }];
        const updated = await getProducts();
        this.products = updated.data;
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

h2 { margin-bottom: 20px; font-size: 22px; }
h3 { margin: 20px 0 12px; font-size: 16px; color: #555; }

.field { margin-bottom: 14px; }
.field label { display: block; margin-bottom: 4px; font-size: 14px; color: #555; }
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
.row-open { z-index: 25; }

/* Объединённая плашка */
.combo {
  display: flex;
  flex: 1;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  min-width: 0;
}

.combo-picker {
  position: relative;
  flex: 1;
  min-width: 0;
}

.combo-trigger {
  width: 100%;
  height: 42px;
  padding: 0 12px;
  text-align: left;
  background: #fff;
  border: none;
  border-right: 1px solid #d1d5db;
  border-radius: 8px 0 0 8px;
  font-size: 14px;
  color: #1a1a2e;
  cursor: pointer;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.combo-trigger:hover { background: #f9fafb; }

.combo-qty {
  flex: 0 0 72px;
  width: 72px;
  padding: 0 8px;
  border: none;
  border-radius: 0 8px 8px 0;
  font-size: 14px;
  text-align: center;
  background: #fff;
  outline: none;
}

.combo:focus-within {
  border-color: #16a34a;
  box-shadow: 0 0 0 3px rgba(22, 163, 74, 0.2);
}

.picker-list {
  position: absolute;
  top: calc(100% + 4px);
  left: 0;
  right: 0;
  max-height: 240px;
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

.picker-option { padding: 8px 12px; font-size: 14px; cursor: pointer; }
.picker-option:hover { background: #f0fdf4; }
.picker-option.selected { background: #dcfce7; }
.picker-empty { padding: 10px 12px; font-size: 14px; color: #6b7280; }

.btn-remove {
  background: none;
  border: none;
  color: #ef4444;
  font-size: 18px;
  cursor: pointer;
  padding: 4px 6px;
  flex-shrink: 0;
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
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
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
  white-space: nowrap;
}
.btn-submit:hover { background: #15803d; }
.btn-submit:disabled { background: #86efac; cursor: not-allowed; }

.total-badge {
  background: #fef3c7;
  color: #92400e;
  padding: 10px 18px;
  border-radius: 8px;
  font-size: 15px;
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  animation: fade-in 0.15s ease;
}

@keyframes fade-in {
  from { opacity: 0; transform: translateX(-6px); }
  to   { opacity: 1; transform: translateX(0); }
}

.result { margin-top: 16px; padding: 12px 16px; border-radius: 8px; font-size: 15px; }
.success { background: #d1fae5; color: #065f46; }
.error { background: #fee2e2; color: #991b1b; }
</style>
