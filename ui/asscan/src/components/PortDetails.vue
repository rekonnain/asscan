<style scoped>
td {
  @apply p-2;
  @apply text-sm;
}
</style>

<template>
  <table class="table-auto">
    <tr class="odd:bg-green-200 even:bg-teal-200" v-for="(val,key) in filteredValues" :key="key">
      <td class="align-top">
        <b>{{ key }}</b>
      </td>
      <td class="align-top p-1" v-if="typeof val === 'string'">
        <img v-if="key === 'screenshot'" :src="'/api/'+val" />
        <pre class="text-xs p-1" v-else>{{val}}</pre>
      </td>
      <td class="align-top pt-1" v-else>
        <KeyValueTable :values="val" />
      </td>
    </tr>
  </table>
</template>


<script>
/* eslint-disable no-console */

import KeyValueTable from "./KeyValueTable";

export default {
  name: "PortDetails",
  props: {
    values: {
      required: true
    }
  },
  components: {
    KeyValueTable
  },

  computed: {
    filteredValues() {
      var foo = this.$props.values;
      delete foo["protocol"];
      delete foo["state"];
      delete foo["ttl"];
      delete foo["reason"];
      delete foo["service"];
      delete foo["port"];
      console.log(foo);
      //   if (Object.keys(foo["script_output"]).length == 0) {
      //     delete foo["script_output"];
      //   }
      return foo;
    }
  }
};
</script>