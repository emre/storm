function Storm($scope) {
  $scope.version = "1.0";
  $scope.state = {
    action: "add new",
    filter: false,
    position: localStorage.getItem("position") == "top" ? "top" : ""
  };

  function plural() {
    $scope.servers.plural = $scope.servers.length > 1 ? "s" : "";
  }

  function focus() {
    var title = document.getElementById("title")
    title.focus();
    title.select();
  }

  $scope.save = function () {

    if (!$scope.title || !$scope.uri) {
       alert("you must fill all fields!");
       return focus();
    }

    var search = $scope.servers.filter(function (server, index) {
      if ($scope.state.editIndex > -1 && $scope.title == server.title) {
        return true;
      } else {
        return $scope.title == server.title;
      }
    }).length;
    if (search > 0) {
      alert("you already have an entry for this server!");
      return focus();
    }

    if ($scope.state.editIndex > -1) {
      $scope.servers[$scope.state.editIndex] = {
        title: $scope.title,
        uri: $scope.uri,
        params: $scope.params
      }
      $scope.title = $scope.uri = "";
      $scope.state.editIndex = -1;
      $scope.state.action = "add new";
      $scope.reset();
      return focus();
    }

    $scope.servers.push({
      title: $scope.title,
      uri: $scope.uri
    });
    plural();
    $scope.title = $scope.uri = "";
    $scope.state.action = "add new";
    focus();
  };

  $scope.reset = function () {
    $scope.servers = $scope.servers.map(function (server) {
      server.editing = false;
      return server;
    });
    plural();
  };

  $scope.toggleTop = function () {
    var current = $scope.state.position;
    var next = current == "top" ? "bottom" : "top";
    localStorage.setItem("position", next);
    $scope.state.position = next;
  };

  $scope.filtered = function (index, filter) {
    if (!filter) return true;
    if (filter && filter.length == 0) return false;
    return $scope.servers[index].title.indexOf(filter) > -1
        || $scope.servers[index].uri.indexOf(filter) > -1;
  };

  $scope.edit = function (server, index) {
    $scope.state.editIndex = index;
    $scope.state.action = "edit " + server.title;
    $scope.title = server.title;
    $scope.uri = server.uri;
    $scope.params = server.params;
    $scope.reset();
    server.editing = true;
    focus();
  };

  $scope.delete = function (serverToDelete) {
    $scope.servers = $scope.servers.filter(function (server) {
      return server.title != serverToDelete.title;
    });
    plural();
    $scope.title = $scope.uri = "";
    $scope.reset();
  };

  $scope.servers = [];

  $scope.reset();
}