import { createStore } from 'vuex'
import axios from 'axios'

const API_URL = 'http://localhost:8000/api'

export default createStore({
  state: {
    testSuites: [],
    testCases: [],
    testRuns: [],
    currentTestRun: null,
    testCaseResults: [],
    testRunTemplates: [],
    loading: false,
    error: null
  },
  mutations: {
    SET_TEST_SUITES(state, testSuites) {
      state.testSuites = testSuites
    },
    SET_TEST_CASES(state, testCases) {
      state.testCases = testCases
    },
    SET_TEST_RUNS(state, testRuns) {
      state.testRuns = testRuns
    },
    SET_CURRENT_TEST_RUN(state, testRun) {
      state.currentTestRun = testRun
    },
    SET_TEST_CASE_RESULTS(state, results) {
      state.testCaseResults = results
    },
    SET_TEST_RUN_TEMPLATES(state, templates) {
      state.testRunTemplates = templates
    },
    SET_LOADING(state, loading) {
      state.loading = loading
    },
    SET_ERROR(state, error) {
      state.error = error
    }
  },
  actions: {
    async fetchTestRunTemplates({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/test-run-templates`)
        if (Array.isArray(response.data)) {
          commit('SET_TEST_RUN_TEMPLATES', response.data)
          commit('SET_ERROR', null)
          console.log(`Fetched ${response.data.length} test run templates`)
        } else {
          console.warn('Expected array response for test run templates, got:', response.data)
          commit('SET_TEST_RUN_TEMPLATES', [])
          commit('SET_ERROR', 'Invalid response format from server')
        }
      } catch (error) {
        commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to fetch test run templates')
        console.error('Error fetching test run templates:', error)
        commit('SET_TEST_RUN_TEMPLATES', [])
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchTestSuites({ commit }) {
      commit('SET_LOADING', true)
      try {
        console.log('Fetching test suites...')
        // First try the standard endpoint
        const response = await axios.get(`${API_URL}/test-suites`)
        
        if (Array.isArray(response.data)) {
          // Process the data to ensure it's in the right format
          const processedData = response.data.map(suite => {
            // Make sure id is a string
            if (suite.id === null || suite.id === undefined) {
              suite.id = String(suite.db_id || '');
            }
            return suite;
          });
          
          if (processedData.length > 0) {
            commit('SET_TEST_SUITES', processedData)
            commit('SET_ERROR', null)
            console.log(`Fetched ${processedData.length} test suites:`, processedData)
          } else {
            // If no test suites found, try a direct query to the database
            console.log("No test suites found, trying direct query...")
            try {
              // Use a custom endpoint that returns raw SQL results
              const directResponse = await axios.get(`${API_URL}/test-suites?raw=true`)
              if (Array.isArray(directResponse.data) && directResponse.data.length > 0) {
                commit('SET_TEST_SUITES', directResponse.data)
                commit('SET_ERROR', null)
                console.log(`Fetched ${directResponse.data.length} test suites via direct query`)
              } else {
                // If still no test suites, create a default one via the API
                console.log("No test suites found, creating a default one...")
                try {
                  const createResponse = await axios.post(`${API_URL}/test-suites`, {
                    id: "DEFAULT",
                    name: "Default Test Suite",
                    format: "json",
                    version: 1,
                    version_string: "1.0",
                    is_final: false
                  })
                  
                  if (createResponse.data) {
                    commit('SET_TEST_SUITES', [createResponse.data])
                    commit('SET_ERROR', null)
                    console.log("Created default test suite:", createResponse.data)
                  } else {
                    commit('SET_TEST_SUITES', [])
                    console.log("Failed to create default test suite")
                  }
                } catch (createError) {
                  console.error("Error creating default test suite:", createError)
                  commit('SET_TEST_SUITES', [])
                }
              }
            } catch (directError) {
              console.error("Error with direct query:", directError)
              commit('SET_TEST_SUITES', [])
            }
          }
        } else {
          console.warn('Expected array response for test suites, got:', response.data)
          commit('SET_TEST_SUITES', [])
          commit('SET_ERROR', 'Invalid response format from server')
        }
      } catch (error) {
        commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to fetch test suites')
        console.error('Error fetching test suites:', error)
        // Set empty array to prevent undefined errors in components
        commit('SET_TEST_SUITES', [])
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchTestCases({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/test-cases`)
        if (Array.isArray(response.data)) {
          commit('SET_TEST_CASES', response.data)
          commit('SET_ERROR', null)
          console.log(`Fetched ${response.data.length} test cases`)
        } else {
          console.warn('Expected array response for test cases, got:', response.data)
          commit('SET_TEST_CASES', [])
          commit('SET_ERROR', 'Invalid response format from server')
        }
      } catch (error) {
        commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to fetch test cases')
        console.error('Error fetching test cases:', error)
        // Set empty array to prevent undefined errors in components
        commit('SET_TEST_CASES', [])
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchTestRuns({ commit }) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/test-runs`)
        if (Array.isArray(response.data)) {
          commit('SET_TEST_RUNS', response.data)
          commit('SET_ERROR', null)
        } else {
          console.warn('Expected array response for test runs, got:', response.data)
          commit('SET_TEST_RUNS', [])
          commit('SET_ERROR', 'Invalid response format from server')
        }
      } catch (error) {
        commit('SET_ERROR', (error.response && error.response.data && error.response.data.detail) || error.message || 'Failed to fetch test runs')
        console.error('Error fetching test runs:', error)
        // Set empty array to prevent undefined errors in components
        commit('SET_TEST_RUNS', [])
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchTestRun({ commit }, id) {
      commit('SET_LOADING', true)
      try {
        const response = await axios.get(`${API_URL}/test-runs/${id}`)
        commit('SET_CURRENT_TEST_RUN', response.data)
        commit('SET_ERROR', null)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch test run')
        console.error('Error fetching test run:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    },
    async fetchTestCaseResults({ commit }, testRunId) {
      commit('SET_LOADING', true)
      try {
        let url = `${API_URL}/test-case-results`
        if (testRunId) {
          url += `?test_run_id=${testRunId}`
        }
        const response = await axios.get(url)
        commit('SET_TEST_CASE_RESULTS', response.data)
        commit('SET_ERROR', null)
      } catch (error) {
        commit('SET_ERROR', error.message || 'Failed to fetch test case results')
        console.error('Error fetching test case results:', error)
      } finally {
        commit('SET_LOADING', false)
      }
    }
  },
  getters: {
    getTestSuiteById: (state) => (id) => {
      return state.testSuites.find(suite => suite.id === id)
    },
    getTestCaseById: (state) => (id) => {
      return state.testCases.find(testCase => testCase.id === id)
    },
    getTestRunById: (state) => (id) => {
      return state.testRuns.find(run => run.id === id)
    },
    getLatestTestRuns: (state) => {
      return state.testRuns.slice().sort((a, b) => b.id - a.id).slice(0, 2)
    },
    getTestRunSummary: (state) => (testRunId) => {
      // Get all results for this test run
      const results = state.testCaseResults.filter(result => result.test_run_id === testRunId);
      
      // Calculate pass/fail statistics
      const total = results.length;
      const passed = results.filter(r => r.result.toLowerCase() === 'pass').length;
      const failed = results.filter(r => r.result.toLowerCase() === 'fail').length;
      const skipped = results.filter(r => r.result.toLowerCase() === 'skip').length;
      const other = total - passed - failed - skipped;
      
      // Calculate pass rate
      const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
      
      return {
        total,
        passed,
        failed,
        skipped,
        other,
        passRate
      };
    }
  }
})
