<template>
  <div id="filters" class="bg-gray-400 p-2">
    <p>Filter</p>
    <div class="filterbox flex">
      Port:
      <input
        type="text"
        class="flex-1 input bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 block w-full appearance-none leading-normal"
        v-model="portfilter"
        placeholder="3389"
        @keyup.enter="port(portfilter)"
      />
    </div>
    <div class="filterbox flex">
      Prefix:
      <input
        v-model="prefixfilter"
        type="text"
        placeholder="192.168.1"
        class="block flex-1 bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 block w-full appearance-none leading-normal"
        @keyup.enter="prefix(prefixfilter)"
      />
    </div>
    <div class="filterbox flex">
      Service:
      <input
        v-model="servicefilter"
        type="text"
        placeholder="http"
        class="block flex-1 bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 block w-full appearance-none leading-normal"
        @keyup.enter="service(servicefilter)"
      />
    </div>
    <div class="filterbox flex">
      Content:
      <input
        v-model="contentfilter"
        type="text"
        placeholder="zyxel"
        class="block flex-1 bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 block w-full appearance-none leading-normal"
        @keyup.enter="content(contentfilter)"
      />
    </div>
    <div class="text-black pt-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline">
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        v-model="vulnsEnabled"
        @click="vulns(vulnsEnabled)"
      />Detected vulns
    </div>
    <div class="text-black py-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline">
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        v-model="screenshotsEnabled"
        @click="screenshots(screenshotsEnabled)"
      />Has screenshots
    </div>
    <div class="text-black py-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline">
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        v-model="hasNotes"
        @click="notes(hasNotes)"
      />Has notes
    </div>
    <div class="text-black py-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline">
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        v-model="hasReadableShares"
        @click="setReadableShares(hasReadableShares)"
      />Read only shares
    </div>
    <div class="text-black py-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline">
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        v-model="hasReadwriteShares"
        @click="setReadwriteShares(hasReadwriteShares)"
      />Read/write shares
    </div>

    <button
      type="button"
      @click="apply()"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold m-1 py-1 px-4 rounded"
    >Apply filters</button>
    <button
      type="button"
      @click="clear()"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold m-1 py-1 px-4 rounded"
    >Clear filters</button>
  </div>
</template>

<script>
/* eslint-disable no-console */

import * as type from "../types";
import Vue from "vue";
import Vuex from "vuex";
Vue.use(Vuex);

export default {
  name: "Filters",
  data() {
    return {
      prefixfilter: "",
      portfilter: "",
      servicefilter: "",
      contentfilter: "",
      vulnsEnabled: false,
      hasNotes: false,
      screenshotsEnabled: false,
      hasReadableShares: false,
      hasReadwriteShares: false
    };
  },
  methods: {
    prefix(prefix) {
      this.$store.dispatch({
        type: type.setPrefix,
        prefix
      });
    },
    port(port) {
      this.$store.dispatch({
        type: type.setPort,
        port
      });
    },
    service(service) {
      this.$store.dispatch({
        type: type.setService,
        service
      });
    },
    content(content) {
      this.$store.dispatch({
        type: type.setContent,
        content
      });
    },
    vulns(vulnsEnabled) {
      this.$store.dispatch({
        type: type.setVulns,
        vulns: vulnsEnabled
      });
    },
    screenshots(screenshotsEnabled) {
      this.$store.dispatch({
        type: type.setScreenshots,
        screenshots: screenshotsEnabled
      });
    },
    readableShares(readableSharesEnabled) {
      this.$store.dispatch({
        type: type.setReadableShares,
        readableShares: readableSharesEnabled
      });
    },
    readwriteShares(readwriteSharesEnabled) {
      this.$store.dispatch({
        type: type.setReadwriteShares,
        readwriteShares: readwriteSharesEnabled
      });
    },
    notes(hasNotes) {
      this.$store.dispatch({
        type: type.setNotes,
        screenshots: hasNotes
      });
    },
    clear() {
      this.prefixfilter = "";
      this.portfilter = "";
      this.servicefilter = "";
      this.contentfilter = "";
      this.$store.dispatch({
        type: type.setContent,
        content: ""
      });
      this.$store.dispatch({
        type: type.setService,
        service: ""
      });
      this.$store.dispatch({
        type: type.setPrefix,
        prefix: ""
      });
      this.$store.dispatch({
        type: type.setPort,
        port: ""
      });
      this.$store.dispatch({
        type: type.setVulns,
        vulns: false
      });
      this.$store.dispatch({
        type: type.setScreenshots,
        screenshots: false
      });
      this.$store.dispatch({
        type: type.setNotes,
        notes: false
      });
      this.$store.dispatch({
        type: type.setReadableShares,
        readableShares: false
      });
      this.$store.dispatch({
        type: type.setReadwriteShares,
        readwriteShares: false
      });
    },
    apply() {
      console.log("apply");
      console.log('content filter is: ' + this.contentfilter)
      this.$store.dispatch({
        type: type.setContent,
        content: this.contentfilter
      });
      this.$store.dispatch({
        type: type.setService,
        service: this.servicefilter
      });
      this.$store.dispatch({
        type: type.setPrefix,
        prefix: this.prefixfilter
      });
      this.$store.dispatch({
        type: type.setPort,
        port: this.portfilter
      });
      this.$store.dispatch({
        type: type.setVulns,
        vulns: this.vulnsEnabled
      });
      this.$store.dispatch({
        type: type.setScreenshots,
        screenshots: this.screenshotsEnabled
      });
      this.$store.dispatch({
        type: type.setNotes,
        notes: this.hasNotes
      });
      this.$store.dispatch({
        type: type.setReadableShares,
        readableShares: this.hasReadableShares
      });
      this.$store.dispatch({
        type: type.setReadwriteShares,
        readwriteShares: this.hasReadwriteShares
      });

    },
    refresh() {
      this.$store.dispatch({
        type: type.refresh,
        dummy: "paska"
      });
    }
  }
};
</script>
