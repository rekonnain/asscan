<style scoped>
td {
  @apply p-2;
}
</style>

<template>
  <table class="table-auto">
    <tr class>
      <td class="bg-red-400 text-center" v-if="values.port.length">
        <b>{{ values.port }}</b>
      </td>
      <td class="bg-green-400 text-center" v-if="values.protocol">
        <b>{{ values.protocol }}</b>
      </td>
      <td class="bg-blue-400 text-center" v-if="values.state">
        <b>{{ values.state }}</b>
      </td>
      <td class="bg-gray-500 text-center" v-if="values.service">
        <b>{{ values.service }}</b>
      </td>
      <td class="bg-gray-100 text-center underline" v-if="url.length > 0">
        <a :href="url" target="_blank">{{url}}</a>
      </td>
    </tr>
  </table>
</template>

<script>
import createurl from "../utils";
export default {
  name: "PortSummary",
  props: {
    values: {
      required: true
    },
    ip: {
      required: true
    }
  },
  computed: {
    url() {
      return createurl.createurl(this.ip, this.values.port);
    }
  }
};
</script>
