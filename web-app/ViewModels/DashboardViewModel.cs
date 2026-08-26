namespace TechScope.ViewModels;

public class DashboardViewModel
{
    public int TotalJobs { get; set; }
    public int TotalTechnologies { get; set; }
    public int TotalCompanies { get; set; }
    public List<TopTechnologyItem> TopTechnologies { get; set; } = new();
    public List<TechnologySearchResult> SearchResults { get; set; } = new();
    public string? SearchString { get; set; }
    public List<jobsByMonthChartData> JobsByMonth { get; set; }
    public List<TechnologyChartData> QuantityTech { get; set; }
    public List<LocationChartData> JobLocations { get; set; }
}

public class TopTechnologyItem
{
    public string Name { get; set; } = string.Empty;
    public int Count { get; set; }
}

public class TechnologySearchResult
{
    public string Name { get; set; } = string.Empty;
}
public class jobsByMonthChartData
{
    public int Mes { get; set; }
    public int Total { get; set; }
}
public class TechnologyChartData
{
    public int Mes { get; set; }

    public string Tecnologia { get; set; }

    public int Total { get; set; }
}
public class LocationChartData
{
    public int Count { get; set; }

    public string Location { get; set; }

}