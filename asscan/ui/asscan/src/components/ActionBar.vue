<template>
  <div class="bg-gray-500 p-2">
    <ScannerState class="float-right" />
    <div class="flex justify-center">
      <button
        @click="scanner()"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold m-1 py-1 px-4 rounded"
      >Scanner</button>
      <button
        @click="results()"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold m-1 py-1 px-4 rounded"
      >Results</button>
    </div>
  </div>
</template>

<script>
import Vue from "vue";
import Vuex from "vuex";
import VueRouter from "vue-router";
import ScannerState from "./ScannerState";
Vue.use(Vuex);
Vue.use(VueRouter);

export default {
  name: "ActionBar",
  components: {
    ScannerState
  },
  methods: {
    scanner() {
      this.$router.push({ name: "scanner" });
    },
    results() {
      this.$router.push({ name: "results" });
    }
  }
};
</script>