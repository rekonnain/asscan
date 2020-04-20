<style scoped>
td {
  @apply px-2;
}
</style>

<template>
  <div>
    <table class="table-auto">
      <tr class="bg-gray-600">
        <td class="text-center">
          <b>nmap</b>
        </td>
        <td class="text-center">
          <b>masscan</b>
        </td>
        <td class="text-center">
          <b>nmap-script</b>
        </td>
        <td class="text-center">
          <b>scraping</b>
        </td>
      </tr>
      <tr class>
        <td class="bg-orange-400 text-center">
          <b>{{ values.nmap }}</b>
        </td>
        <td class="bg-green-400 text-center">
          <b>{{ values.masscan }}</b>
        </td>
        <td class="bg-blue-400 text-center">
          <b>{{ values.vuln }}</b>
        </td>
        <td class="bg-pink-500 text-center">
          <b>{{ values.scrapers }}</b>
        </td>
      </tr>
    </table>
  </div>
</template>

<script>
/* eslint-disable no-console */

import Vue from "vue";
import VueRouter from "vue-router";
Vue.use(VueRouter);
import axios from "axios";

export default {
  name: "Scanner",
  data() {
    return {
      values: {
        nmap: "",
        masscan: "",
        nmapscript: "",
        scraping: ""
      },
      poller: ""
    };
  },
  methods: {
    async update() {
      const status = await axios.get("/api/jobs/overview");
      this.poller = setTimeout(() => {
        this.update();
      }, 5000);
      this.values = status.data;
    }
  },
  mounted() {
    this.update();
  },
  destroyed() {
    console.log("Menin pois ja clearing " + this.poller);
    clearTimeout(this.poller);
  }
};
</script>