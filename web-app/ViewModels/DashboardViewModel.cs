namespace TechScope.ViewModels;

public class DashboardViewModel
{
    public int TotalJobs { get; set; }
    public int TotalTechnologies { get; set; }
    public int TotalCompanies { get; set; }
    public List<TechnologySearchResult> SearchResults { get; set; } = new();
    public string? SearchString { get; set; }
    public List<TechnologyChartData> QuantityTech { get; set; }
    public List<LocationChartData> JobLocations { get; set; }
    public List<TopTechnologyItem> TopTechnologies { get; set; } = new();
    public List<TechMarketSharesItem> TechMarketShares { get; set; } = new();
    public int PageNumber { get; set; }
    public int PageSize { get; set; }
    public int TotalPages => (int)Math.Ceiling((double)TotalJobs / PageSize);
}

public class TopTechnologyItem
{
    public string Name { get; set; } = string.Empty;
    public int Count { get; set; }
}
public class TechMarketSharesItem
{
    public string Name { get; set; } = string.Empty;
    public int MarketShares { get; set; }
}

public class TechnologySearchResult
{
    public string Name { get; set; } = string.Empty;
}
public class TechnologyChartData
{
    public DateOnly? Data { get; set; }

    public string Tecnologia { get; set; }

    public int Total { get; set; }
}
public class LocationChartData
{
    public int Count { get; set; }

    public string Location { get; set; }

}