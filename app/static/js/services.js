angular.module("app")
.filter('linkyWithHtml', function($filter) {
  return function(value) {
    let linked = $filter('linky')(value);
    if (linked != undefined)
    	return replaced = linked.replace(/\&gt;/g, '>').replace(/\&lt;/g, '<');
    else
    	return "";
  };
})