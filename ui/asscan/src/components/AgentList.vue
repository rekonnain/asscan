<template>
  <div>
      Agents<br/>
    <div
      class="text-black pt-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline"
    >
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        v-model="mainAgentEnabled"
        @click="mainAgentEnabled = !mainAgentEnabled"
      />Detected vulns
    </div>

    <div
      v-for="agent in agents"
      :key="agent"
      class="text-black pt-1 px-2 m-2 rounded focus:outline-none focus:shadow-outline"
    >
      <input
        type="checkbox"
        class="mr-1 bg-gray-300 text-gray-800 py-2 px-4 rounded-l"
        @click="toggleAgent(agent)"
      />Detected vulns
    </div>
  </div>
</template>

<script>
/* eslint-disable no-console */
/* eslint-disable no-unused-vars */

import axios from "axios";
import * as type from "../types";
import Vue from "vue";
import Vuex from "vuex";
Vue.use(Vuex);

export default {
    name: "AgentList",
    data() {
        return {
            mainAgentEnabled: true,
            agents: {}
        }
    },

    async getAgents() {
        const agents = await axios.get("/api/agents/")
        this.agents = agents.data.clients;
    },
    toggleAgent(agent) {
        console.log(agent)
    },

    mounted() {
        console.log("agents")
        this.getAgents();
    }
}
</script>
