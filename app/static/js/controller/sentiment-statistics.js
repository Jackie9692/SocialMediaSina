angular.module("app").controller("SentimentStatisticsCtrl", function ($scope, sentimentStatisticsService) {
	$scope.state = sentimentStatisticsService;
	sentimentStatisticsService.generate()
	$scope.version = true;
	$scope.$watch("state.loading", function(current, previous) {
		chart();
	});

	$scope.$watch("version", function(current, previous) {
		chart();
	});

	chart = function() {		
		if ($scope.version) {
			chartV1();
		}
		else {
			chartV2();
		}
	}

	chartV1 = function() {
		negative = [];
		positive = [];
		min = [];
		diff = [];

		for (i in $scope.state.data.date) {
			negative.push($scope.state.data.negative_status[i] + $scope.state.data.negative_comment[i]);
			positive.push($scope.state.data.positive_status[i] + $scope.state.data.positive_comment[i]);
			min.push(Math.min(negative[i], positive[i]));
			if (negative[i] < positive[i]) {
				diff.push({value : positive[i] - negative[i] , itemStyle:{ normal:{color:'green'}}})
			}
			else {
				diff.push({value : negative[i] - positive[i], itemStyle:{ normal:{color:'red'}}})
			}
		}

		require.config({
			paths: {
				echarts: 'http://echarts.baidu.com/build/dist'
			}
		});

		// use
		require(
			[
				'echarts',
				'echarts/chart/line',
				'echarts/chart/bar' // require the specific chart type
			],
			function (ec) {
				// Initialize after dom ready
				var myChart = ec.init(document.getElementById('main')); 
				
				var option = {
					tooltip : {
						trigger: 'axis',
						formatter: function (params){
							console.log(params)	
							return params[0].name + '<br/>'
								 + params[2].seriesName + ' : ' + params[2].value + '<br/>'
								 + params[3].seriesName + ' : ' + params[3].value + '<br/>'
								 + 'difference : ' + (params[2].value - params[1].value > 0 ? '+' : '-') 
								 + params[0].value + '<br/>'
						}
					},
					legend: {
						data:['positive', 'negative'],
						selectedMode:false
					},
					xAxis : [
						{
							type : 'category',
							data : $scope.state.data.date
						}
					],
					yAxis : [
						{
							type : 'value',
						}
					],
					series : [
						{
							name:'positive',
							type:'line',
							data: positive
						},
						{
							name:'negative',
							type:'line',
							data: negative
						},
						{
							name:'min',
							type:'bar',
							stack: '1',
							barWidth: 6,
							itemStyle:{
								normal:{
									color:'rgba(0,0,0,0)'
								},
								emphasis:{
									color:'rgba(0,0,0,0)'
								}
							},
							data: min 
						},
						{
							name:'diff',
							type:'bar',
							stack: '1',
							data: diff
						}
					]
				};

				// Load data into the ECharts instance 
				myChart.setOption(option); 
			}
		);

	}

	chartV2 = function() {
		require.config({
			paths: {
				echarts: 'http://echarts.baidu.com/build/dist'
			}
		});

		// use
		require(
			[
				'echarts',
				'echarts/chart/bar' // require the specific chart type
			],
			function (ec) {
				// Initialize after dom ready
				var myChart = ec.init(document.getElementById('main')); 
				
				var option = {
					tooltip : {
						trigger: 'axis',
						axisPointer : {
							type : 'shadow'
						}
					},
					legend: {
						data:['negative_status','negative_comment','neuter_status','neuter_comment','positive_status','positive_comment']
					},
					calculable : true,
					xAxis : [
						{
							type : 'category',
							data : $scope.state.data.date
						}
					],
					yAxis : [
						{
							type : 'value'
						}
					],
					series : [
						{
							name:'negative_status',
							type:'bar',
							stack: 'negative',
							data: $scope.state.data.negative_status
						},
						{
							name:'negative_comment',
							type:'bar',
							stack: 'negative',
							data: $scope.state.data.negative_comment
						},
						{
							name:'neuter_status',
							type:'bar',
							stack: 'neuter',
							data: $scope.state.data.neuter_status
						},
						{
							name:'neuter_comment',
							type:'bar',
							stack: 'neuter',
							data: $scope.state.data.neuter_comment
						},
						{
							name:'positive_status',
							type:'bar',
							stack: 'positive',
							data: $scope.state.data.positive_status
						},
						{
							name:'positive_comment',
							type:'bar',
							stack: 'positive',
							data: $scope.state.data.positive_comment
						},
					]
				};
				// Load data into the ECharts instance 
				myChart.setOption(option); 
			}
		);
	}
})

.service('sentimentStatisticsService', function($http) {
	var data = {
		date: [],
		negative_status: [],
		negative_comment: [],
		neuter_status: [],
		neuter_comment: [],
		positive_status: [],
		positive_comment: [],
	};

	var loading = true;

	var params = {};

	return {
		data: data,
		loading: loading,

		setParams: function(state) {
			params = state;
		},
		generate: function() {
			if (params != undefined) {
				scope = this

				this.loading = true;

				params.request = "sentimentStatistics";

				console.log("Sending search request to sever");
				$http({
					url: "search_request", 
					method: "GET",
					params: params
				}).then(function(response) {
					console.log("Receiving answer");
					console.log(response.data)
					scope.data = response.data.data;

					scope.loading = false;
				});
				return true;
			}
			return false;
		},
	};
});

