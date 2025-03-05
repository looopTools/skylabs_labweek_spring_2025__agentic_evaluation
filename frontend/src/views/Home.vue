<template>
  <div class="home">
    <h1>QA Database System</h1>
    <div class="dashboard">
      <div class="stats">
        <div class="stat-card">
          <h3>Test Suites</h3>
          <p class="stat-number">{{ testSuites.length }}</p>
        </div>
        <div class="stat-card">
          <h3>Test Cases</h3>
          <p class="stat-number">{{ testCases.length }}</p>
        </div>
        <div class="stat-card">
          <h3>Test Runs</h3>
          <p class="stat-number">{{ testRuns.length }}</p>
        </div>
      </div>
      
      <div class="recent-activity">
        <h2>Recent Test Runs</h2>
        <div v-if="loading">Loading...</div>
        <div v-else-if="error">{{ error }}</div>
        <div v-else-if="testRuns.length === 0">No test runs available</div>
        <div v-else class="recent-runs">
          <div v-for="run in recentTestRuns" :key="run.id" class="run-card">
            <div class="run-header">
              <h3>Test Run #{{ run.id }}</h3>
              <span :class="['status-badge', run.status.toLowerCase()]">{{ run.status }}</span>
            </div>
            
            <div class="run-summary">
              <div class="summary-stats">
                <div class="stat">
                  <span class="stat-label">Pass Rate</span>
                  <span class="stat-value" :class="getPassRateClass(getRunSummary(run.id).passRate)">
                    {{ getRunSummary(run.id).passRate }}%
                  </span>
                </div>
                
                <div class="stat-pills">
                  <span class="pill pass">{{ getRunSummary(run.id).passed }} Passed</span>
                  <span class="pill fail">{{ getRunSummary(run.id).failed }} Failed</span>
                  <span v-if="getRunSummary(run.id).skipped > 0" class="pill skip">
                    {{ getRunSummary(run.id).skipped }} Skipped
                  </span>
                </div>
              </div>
              
              <div class="progress-bar">
                <div class="progress pass" :style="{width: `${getRunSummary(run.id).passRate}%`}"></div>
                <div class="progress fail" :style="{width: `${getRunSummary(run.id).failed / getRunSummary(run.id).total * 100}%`}"></div>
                <div class="progress skip" :style="{width: `${getRunSummary(run.id).skipped / getRunSummary(run.id).total * 100}%`}"></div>
              </div>
            </div>
            
            <div class="run-footer">
              <p class="timestamp" v-if="run.created_at">
                Run on {{ new Date(run.created_at).toLocaleString() }}
              </p>
              <router-link :to="`/test-runs/${run.id}`" class="view-details">View Details</router-link>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import { computed, onMounted } from 'vue'
import { useStore } from 'vuex'

export default {
  name: 'Home',
  setup() {
    const store = useStore()
    
    onMounted(() => {
      store.dispatch('fetchTestSuites')
      store.dispatch('fetchTestCases')
      store.dispatch('fetchTestRuns')
      store.dispatch('fetchTestCaseResults')
    })
    
    const testSuites = computed(() => store.state.testSuites)
    const testCases = computed(() => store.state.testCases)
    const testRuns = computed(() => store.state.testRuns)
    const loading = computed(() => store.state.loading)
    const error = computed(() => store.state.error)
    
    const recentTestRuns = computed(() => {
      return testRuns.value
        .slice()
        .sort((a, b) => b.id - a.id)
        .slice(0, 2)  // Show only the 2 most recent runs
    })
    
    const getRunSummary = (runId) => {
      return store.getters.getTestRunSummary(runId);
    }
    
    const getPassRateClass = (rate) => {
      if (rate >= 90) return 'excellent';
      if (rate >= 75) return 'good';
      if (rate >= 50) return 'average';
      return 'poor';
    }
    
    return {
      testSuites,
      testCases,
      testRuns,
      loading,
      error,
      recentTestRuns,
      getRunSummary,
      getPassRateClass
    }
  }
}
</script>

<style scoped>
.dashboard {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  max-width: 1200px;
  margin: 0 auto;
  padding: 1rem;
}

.stats {
  display: flex;
  justify-content: space-around;
  gap: 1rem;
}

.stat-card {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  flex: 1;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.stat-number {
  font-size: 2rem;
  font-weight: bold;
  color: #42b983;
}

.recent-activity {
  background-color: #f5f5f5;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.recent-runs {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
  gap: 1.5rem;
  margin-top: 1rem;
}

.run-card {
  background-color: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.run-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  border-bottom: 1px solid #eee;
  padding-bottom: 0.75rem;
}

.status-badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.875rem;
  font-weight: bold;
  text-transform: uppercase;
}

.status-badge.completed {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.status-badge.failed {
  background-color: #ffebee;
  color: #c62828;
}

.status-badge.running {
  background-color: #e3f2fd;
  color: #1565c0;
}

.run-summary {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.summary-stats {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.stat {
  display: flex;
  flex-direction: column;
}

.stat-label {
  font-size: 0.875rem;
  color: #666;
}

.stat-value {
  font-size: 1.5rem;
  font-weight: bold;
}

.stat-value.excellent {
  color: #2e7d32;
}

.stat-value.good {
  color: #689f38;
}

.stat-value.average {
  color: #ffa000;
}

.stat-value.poor {
  color: #d32f2f;
}

.stat-pills {
  display: flex;
  gap: 0.5rem;
}

.pill {
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: bold;
}

.pill.pass {
  background-color: #e8f5e9;
  color: #2e7d32;
}

.pill.fail {
  background-color: #ffebee;
  color: #c62828;
}

.pill.skip {
  background-color: #f5f5f5;
  color: #757575;
}

.progress-bar {
  height: 0.5rem;
  background-color: #f5f5f5;
  border-radius: 0.25rem;
  overflow: hidden;
  display: flex;
}

.progress {
  height: 100%;
}

.progress.pass {
  background-color: #4caf50;
}

.progress.fail {
  background-color: #f44336;
}

.progress.skip {
  background-color: #9e9e9e;
}

.run-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 0.5rem;
  border-top: 1px solid #eee;
  padding-top: 0.75rem;
}

.timestamp {
  font-size: 0.875rem;
  color: #666;
  margin: 0;
}

.view-details {
  color: #1976d2;
  text-decoration: none;
  font-weight: 500;
}

.view-details:hover {
  text-decoration: underline;
}

h1 {
  margin-bottom: 2rem;
}

h2 {
  margin-bottom: 1rem;
}

h3 {
  margin: 0;
}
</style>
