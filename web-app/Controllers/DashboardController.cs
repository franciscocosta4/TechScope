using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TechScope.Data;
using TechScope.ViewModels;

namespace TechScope.Controllers;

public class DashboardController : Controller
{
    private readonly ApplicationDbContext _context;

    public DashboardController(ApplicationDbContext context)
    {
        _context = context;
    }

    public async Task<IActionResult> Index(string? searchString, int pageNumber = 1, int pageSize = 10)
    {
        var totalJobs = await _context.Jobs.CountAsync();
        var totalCompanies = await _context.Companies.CountAsync();

        var totalTechnologies = await _context.JobKeywords
            .Where(jk => jk.Category == "technology")
            .Select(jk => jk.Keyword)
            .Distinct()
            .CountAsync();

        var topTechnologies = await _context.JobKeywords
            .Where(jk => jk.Category == "technology")
            .GroupBy(jk => jk.Keyword)
            .OrderByDescending(g => g.Count())
            .Skip((pageNumber - 1) * pageSize)
            .Take(pageSize)
            .Select(g => new TopTechnologyItem
            {
                Name = g.Key,
                Count = g.Count()
            })
            .ToListAsync();

        var techMarketShares  =  await _context.JobKeywords
            .Where(jk => jk.Category == "technology")
            .GroupBy(jk => jk.Keyword)
            .OrderByDescending(g => g.Count())
            // .Take(20)
            .Select(g => new TechMarketSharesItem
            {
                Name = g.Key,
                MarketShares =  100 * g.Count() / totalJobs
            })
            .Where(x => x.MarketShares > 0)
            .ToListAsync();


        var jobLocations =  _context.Jobs //pie de locations
            .Where(j => j.Location != null)
            .GroupBy(jk => jk.Location)
            .OrderByDescending(g => g.Count())
            .Take(10) 
            .Select(g => new LocationChartData
            {
                Location = g.Key,
                Count = g.Count()
            })
            .ToList();

        var tecnologiasSelecionadas = new[]
        {
            ".net",
            "nodejs",
            "postgresql",
            "mongodb",
            "c#",
            "java",
            "spring",
            "javascript",
            "typescript",
            "angular",
            "react",
            "python",
            "laravel",
            "php",
            "aws",
            "azure",
            "docker",
        };
        var quantityTech = _context.JobKeywords // serve para o grafico de tecnologias
            .Where(jk =>
                jk.Category == "technology" &&
                jk.Job.DatePosted.HasValue &&
                tecnologiasSelecionadas.Contains(jk.Keyword.ToLower()))
            .GroupBy(jk => new
            {
                Data = jk.Job.DatePosted,
                Tecnologia = jk.Keyword
            })
            .Select(g => new TechnologyChartData
            {
                Data = g.Key.Data,
                Tecnologia = g.Key.Tecnologia,
                Total = g.Count()
            })
            .OrderBy(x => x.Data)
            .ThenBy(x => x.Tecnologia)
            .ToList();

        var model = new DashboardViewModel
        {
            TotalJobs = totalJobs,
            TotalTechnologies = totalTechnologies,
            TotalCompanies = totalCompanies,
            TopTechnologies = topTechnologies,
            TechMarketShares = techMarketShares,
            SearchString = searchString,
            QuantityTech = quantityTech,
            JobLocations = jobLocations,
            PageNumber = pageNumber,
            PageSize = pageSize
        };

        if (!string.IsNullOrWhiteSpace(searchString))
        {
            var term = searchString.Trim();
            model.SearchResults = await _context.JobKeywords
                .Where(jk => jk.Category == "technology" && jk.Keyword != null && jk.Keyword.ToUpper().Contains(term.ToUpper()))
                .Select(jk => jk.Keyword)
                .Distinct()
                .OrderBy(k => k)
                .Select(k => new TechnologySearchResult
                {
                    Name = k!
                })
                .ToListAsync();
        }

        return View(model);
    }
}
