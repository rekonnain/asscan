<template>
  <div class="p-2">
    <button
      type="button"
      @click="refresh()"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold m-1 py-1 px-4 rounded"
    >Refresh</button>

    <h3>Hosts:</h3>
    <div v-for="ip in hosts" :key="ip">
      <div @click="selectIp(ip)" class="cursor-pointer hover:underline">>{{ ip }}</div>
    </div>
  </div>
</template>

<script>
/* eslint-disable no-console */

import axios from "axios";
import Vue from "vue";
import Vuex from "vuex";
import * as type from "../types.js";
import VueRouter from "vue-router";

Vue.use(Vuex);
Vue.use(VueRouter);

export default {
  name: "HostList",
  data() {
    return {
      hosts: []
    };
  },
  computed: {
    prefix() {
      return this.$store.state.prefixFilter;
    },
    port() {
      return this.$store.state.portFilter;
    },
    service() {
      return this.$store.state.serviceFilter;
    },
    vulns() {
      return this.$store.state.vulns;
    },
    screenshots() {
      return this.$store.state.screenshots;
    },
    notes() {
      return this.$store.state.notes;
    },
    content() {
      return this.$store.state.contentFilter
    }
  },
  methods: {
    selectIp(ip) {
      this.$router.replace({ name: "results", params: { ip: ip } });
      this.$store.dispatch({
        type: type.selectIp,
        ip
      });
    },
    async fetchAll() {
      const hostlist = await axios.get("/api/results/ips/");
      this.hosts = hostlist.data["ips"];
    },
    refresh() {
      this.updateAnyway();
    },
    async updateWithContent(content) {
      console.log('vittu content = ' + content)
      const hostlist = await axios.get(
        "/api/results/filter?content=" +
          content +
          "&prefix=" +
          this.$store.state.prefixFilter +
          "&port=" +
          this.$store.state.portFilter +
          "&service=" +
          this.$store.state.serviceFilter +
          "&vulns=" +
          this.$store.state.vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + this.$store.state.notes
      );
      this.hosts = hostlist.data["ips"];
    },
    async updateWithPrefix(prefix) {
      const hostlist = await axios.get(
        "/api/results/filter?prefix=" +
          prefix +
          "&port=" +
          this.$store.state.portFilter +
          "&service=" +
          this.$store.state.serviceFilter +
          "&vulns=" +
          this.$store.state.vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + this.$store.state.notes
          + "&content=" + this.$store.state.contentFilter
      );
      this.hosts = hostlist.data["ips"];
    },
    async updateWithPort(port) {
      const hostlist = await axios.get(
        "/api/results/filter?port=" +
          port +
          "&prefix=" +
          this.$store.state.prefixFilter +
          "&service=" +
          this.$store.state.serviceFilter +
          "&vulns=" +
          this.$store.state.vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + this.$store.state.notes
          + "&content=" + this.$store.state.contentFilter
      );
      this.hosts = hostlist.data["ips"];
    },
    async updateWithService(service) {
      const hostlist = await axios.get(
        "/api/results/filter?port=" +
          this.$store.state.portFilter +
          "&prefix=" +
          this.$store.state.prefixFilter +
          "&service=" +
          service +
          "&vulns=" +
          this.$store.state.vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + this.$store.state.notes
          + "&content=" + this.$store.state.contentFilter
      );
      this.hosts = hostlist.data["ips"];
    },
    async updateWithNotes(notes) {
      const hostlist = await axios.get(
        "/api/results/filter?port=" +
          this.$store.state.portFilter +
          "&prefix=" +
          this.$store.state.prefixFilter +
          "&service=" +
          this.$store.state.serviceFilter +
          "&vulns=" +
          this.$store.state.vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + notes
          + "&content=" + this.$store.state.contentFilter
      );
      this.hosts = hostlist.data["ips"];
    },
    async updateAnyway() {
      console.log('vittu content = ' + this.$store.state.content)
      const hostlist = await axios.get(
        "/api/results/filter?port=" +
          this.$store.state.portFilter +
          "&prefix=" +
          this.$store.state.prefixFilter +
          "&service=" +
          this.$store.state.serviceFilter +
          "&vulns=" +
          this.$store.state.vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + this.$store.state.notes
          + "&content=" + this.$store.state.contentFilter
      );
      this.hosts = hostlist.data["ips"];
    },
    async updateWithVulns(vulns) {
      const hostlist = await axios.get(
        "/api/results/filter?port=" +
          this.$store.state.portFilter +
          "&prefix=" +
          this.$store.state.prefixFilter +
          "&service=" +
          this.$store.state.serviceFilter +
          "&vulns=" +
          vulns +
          "&screenshots=" +
          this.$store.state.screenshots +
          "&notes=" + this.$store.state.notes
          + "&content=" + this.$store.state.contentFilter
      );
      this.hosts = hostlist.data["ips"];
    }
  },
  watch: {
    prefix(prefix) {
      this.updateWithPrefix(prefix);
    },
    port(port) {
      this.updateWithPort(port);
    },
    service(service) {
      this.updateWithService(service);
    },
    vulns(vulns) {
      this.updateWithVulns(vulns);
    },
    notes(notes) {
      this.updateWithNotes(notes);
    },
    content(content) {
      console.log('slerba')
      this.updateWithContent(content);
    },
    refresh() {
      console.log("vittu");
    }
  },

  async mounted() {
    const hostlist = await axios.get("/api/results/ips/");
    this.hosts = hostlist.data["ips"];
  }
};
</script>
