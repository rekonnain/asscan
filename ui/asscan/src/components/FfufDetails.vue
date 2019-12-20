<style scoped>
td {
  @apply px-2;
  @apply py-1;
}
</style>

<template>
  <table class="table-auto">
    <tr class="bg-blue-500">
      <td class>
        <b>Position</b>
      </td>
      <td class>
        <b>Length</b>
      </td>
      <td class>
        <b>Words</b>
      </td>
      <td class>
        <b>Status</b>
      </td>
      <td class>
        <b>Input</b>
      </td>
    </tr>
    <tr v-for="row in values.results" :key="row" class="even:bg-blue-300 odd:bg-blue-200">
      <td>{{ row.position }}</td>
      <td>{{ row.length }}</td>
      <td>{{ row.words }}</td>
      <td>{{ row.status }}</td>
      <td>
        <a target="_blank" :href="baseurl + row.input">
          <pre class="underline text-xs">{{row.input}}</pre>
        </a>
      </td>
    </tr>
  </table>
</template>


<script>
/* eslint-disable no-console */

// ffuf word entries look like
// {
//     "input": "",
//     "length": 10918,
//     "position": 0,
//     "status": 200,
//     "words": 3499
// },

export default {
  name: "Ffuf",
  props: {
    values: {
      required: true
    },
    baseurl: {
      required: true
    }
  },
  mounted() {
    console.log("ffuf");
    console.log(this.values);
  }
};
</script>