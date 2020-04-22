<style scoped>
td {
  @apply p-2;
  @apply text-sm;
}
</style>

<template>
  <table class="table-auto">
    <tr class="even:bg-blue-300 odd:bg-indigo-300" v-for="(val,key) in values" :key="key">
      <td class="align-top w-1/4">
        <b>{{ key }}</b>
      </td>
      <td class="align-top w-3/4 md:overflow-x-scroll" v-if="typeof val === 'string'">
        <pre class="text-xs">{{val}}</pre>
      </td>
      <td v-else>x</td>
    </tr>
  </table>
</template>

<script>
/* eslint-disable no-console */
export default {
  name: "KeyValueTable",
  props: {
    values: {
      required: true
    }
  },
  mounted() {
    console.log("kvt");
    console.log(this.values);
  }
};
</script>
