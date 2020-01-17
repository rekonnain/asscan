<template>
  <div id="host-details-list">

  <div v-if="results[0]">
    <h2>{{ results[0]['ipv4']}}</h2>
    <p>
      <a class="underline" :href="'/api/results/ip/'+results[0]['ipv4']">Raw data</a>
    </p>

    <div class="m-2 p-2 bg-gray-400">
      <p>Notes</p>
      <div v-if="note">
        {{ note }}
            <button
      type="button"
      @click="removenote()"
      class="bg-blue-500 hover:bg-blue-700 text-white font-bold m-1 px-4 rounded"
    >Delete note</button>

      </div>
      <div v-else>
      <input
        v-model="note"
        type="text"
        placeholder="Add a note here"
        class="block flex-1 bg-white focus:outline-none focus:shadow-outline border border-gray-300 rounded-lg ml-2 py-1 px-2 block w-full appearance-none leading-normal"
        @keyup.enter="addnote(note)"
      />
      </div>
      </div>

    <div class="m-2 p-2 bg-gray-400" v-for="result in results" :key="result['ipv4']">
      <p v-if="result['scantype']">Scan type: {{result['scantype']}}</p>
      <p v-if="result['cmdline']">Scanner args: <pre class="text-xs">{{result['cmdline']}}</pre></p>
      <p v-if="result['scantime']">Scan time: {{result['scantime']}}</p>
      <p v-if="result['jobid']">Job ID: {{result['jobid']}}</p>
      <p v-if="result['scantype'] == 'masscan'">
        Open ports:
        <b class="pl-2" v-for="x in result['ports']" :key="x">
          <span v-if="createurl(results[0]['ipv4'], x['port']).length > 0">
            <a class="underline" target="_blank" :href="createurl(results[0]['ipv4'], x['port'])">{{x['port']}}</a>
          </span>
          <span v-else>
          {{x['port']}}
          </span>
          </b>
      </p>
      <div v-if="result['scantype'] == 'bluekeep'  || result['scantype'] == 'ms17_010'">
        <div v-for="(portvals) in result['ports']" :key="portvals">
          <PortSummary :values="portvals" :ip="results[0]['ipv4']" class="mt-6" />
          <PortDetails :values="portvals" />
        </div>
      </div>
      <div v-if="result['scantype'] == 'nmap'">
        <div v-for="(portvals) in result['ports']" :key="portvals">
          <PortSummary :values="portvals" :ip="results[0]['ipv4']" class="mt-6" />
          <PortDetails :values="portvals" />
        </div>
      </div>
      <div v-else-if="result['scantype'].includes('screenshot')">
        <div v-for="(portvals, port) in result['ports']" :key="port">
          <img :src="'/api/'+portvals.file" />
        </div>
      </div>
      <div v-else-if="result['scantype'].includes('enum4linux')">
        <div v-for="(portvals, port) in result['ports']" :key="port" class="object-fill">
          <div class="flex justify-center" style="height: 480px">
          <iframe :src="'/api/'+portvals.file" class="object-fill" style="position: relative; height: 100%; width: 100%;" />
          </div>
        </div>
      </div>
      <div v-else-if="result['scantype'].includes('snmpwalk')">
        <div v-for="(portvals, port) in result['ports']" :key="port" class="object-fill">
          <div class="flex justify-center" style="height: 480px">
          <iframe :src="'/api/'+portvals.file" class="object-fill" style="position: relative; height: 100%; width: 100%;" />
          </div>
        </div>
      </div>
      <div v-else-if="result['scantype'] == 'ffuf'">
        <div v-for="(portvals, idx) in result['ports']" :key="idx">
          <FfufDetails :values="portvals" :baseurl="'http://'+results[0]['ipv4']+':'+portvals['port']"/>
        </div>
      </div>
      <div v-if="result['scripts']">
        <KeyValueTable :values="result['scripts']"/>
      </div>
      <div v-if="result['osmatches']" class="mt-8">
        <p>Guessed operating system:</p>
        <div v-for="osmatches in result['osmatches']" :key="osmatches['name']">
          {{ osmatches.accuracy }}% {{ osmatches.name }}
        </div>
      </div>
    </div>
  </div>

  </div>
</template>

<script>
/* eslint-disable no-console */
/* eslint-disable no-unused-vars */

import axios from "axios";
import KeyValueTable from "./KeyValueTable";
import PortSummary from "./PortSummary";
import PortDetails from "./PortDetails";
import FfufDetails from "./FfufDetails";
import utils from '../utils.js'
import Vue from 'vue'
import VueRouter from "vue-router";
Vue.use(VueRouter)

export default {
  name: "HostList",
  components: {
    KeyValueTable,
    PortSummary,
    PortDetails,
    FfufDetails
  },
  data() {
    return {
      results: []
    };
  },

  computed: {
    currentIp() {
      return this.$store.state.currentIp;
    }
  },

  methods: {
    selectIp(ip) {
        this.getNotes(ip)
      axios
        .get("/api/results/ip/" + ip)
        .then(response => this.handleResults(response.data, ip));
    },
    handleResults(results, ip) {
      console.log("All shit")
      console.log(results[ip])
      this.results = results[ip];
    },
    createurl: utils.createurl,
    getNotes(ip) {
      axios
      .get("/api/notes/ip/" + ip)
      .then(response => this.handleNotes(response.data, ip));
    },
    handleNotes(notes, ip) {
      console.log("notes:")
      console.log(notes[ip])
      this.note = notes[ip]
    },
    addnote(note) {
      const ip = this.$store.state.currentIp
      console.log(ip)
      const data = { [ip]: note }
      axios.post("/api/notes/", data)
      .then(this.selectIp(this.$store.state.currentIp))
    },
    removenote() {
      this.note = false
      axios.delete("/api/notes/" + this.$store.state.currentIp)
      .then(this.selectIp(this.$store.state.currentIp))
    }
  },

  watch: {
    currentIp(ip) {
      this.selectIp(ip);
    },
        $route(to, from) {
      console.log('to / from')
      console.log(to)
      console.log(from)
      this.selectIp(to.params.ip)
    }

  },

  async mounted() {
    if (this.$store.state.currentIp.length > 0) {
    this.selectIp(this.$store.state.currentIp);
    }
  }
};
</script>
