<template>
  <div>
    <OrderForm @orders-changed="onOrdersChanged" />
    <OrdersList ref="ordersList" />
  </div>
</template>

<script>
import OrderForm from "../components/OrderForm.vue";
import OrdersList from "../components/OrdersList.vue";

export default {
  name: "OrdersView",
  components: { OrderForm, OrdersList },
  methods: {
    onOrdersChanged() {
      this.$refs.ordersList?.load();
    },
  },
};
</script>
