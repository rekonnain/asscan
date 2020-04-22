<template>
  <div id="app" class="h-screen flex flex-col font-sans">
    <ActionBar />

    <div class="md:flex flex-grow md:overflow-hidden">
      <div class="bg-gray-300 flex-none w-full md:max-w-xs md:overflow-x-scroll">
        <Filters />
        <HostList />
      </div>
      <div class="bg-gray-100 flex-1 md:overflow-x-scroll">
        <div class="p-2">
          <router-view>
            <ScannerState />
          </router-view>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
/* eslint-disable vue/no-unused-components */
import HostList from "./components/HostList.vue";
import HostDetailsList from "./components/HostDetailsList.vue";
import Filters from "./components/Filters.vue";
import ActionBar from "./components/ActionBar";
import ScannerState from "./components/ScannerState";
import * as type from "./types.js";

export default {
  name: "app",
  components: {
    HostDetailsList,
    HostList,
    Filters,
    ScannerState,
    ActionBar
  },
  methods: {
    port(port) {
      alert("foobar " + port);
    },
    prefix(prefix) {
      alert("asdf " + prefix);
      this.$store.dispatch({
        type: type.setPrefix,
        prefix
      });
    }
  },
  mounted() {
    this.$router.replace({ name: "scannerstate" });
  }
};
</script>

<style>
.filterbox {
  margin: 2px;
  padding: 2px;
}
.input {
  min-width: 20px;
  width: 30px;
}
</style>
