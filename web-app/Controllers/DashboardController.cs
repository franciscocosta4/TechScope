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

    public async Task<IActionResult> Index(string? searchString)
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
            .Take(10)
            .Select(g => new TopTechnologyItem
            {
                Name = g.Key,
                Count = g.Count()
            })
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
    "react native",
    "sql",
    "c#",
    "java",
    "javascript",
    "typescript",
    "angular",
    "react",
    "nodejs",
    "python",
    "laravel",
    "php",
};
        var quantityTech = _context.JobKeywords // serve para o grafico de tecnologias
            .Where(jk =>
                jk.Category == "technology" &&
                jk.Job.DatePosted.HasValue &&
                tecnologiasSelecionadas.Contains(jk.Keyword.ToLower()))
            .GroupBy(jk => new
            {
                Mes = jk.Job.DatePosted.Value.Month,
                Tecnologia = jk.Keyword
            })
            .Select(g => new TechnologyChartData
            {
                Mes = g.Key.Mes,
                Tecnologia = g.Key.Tecnologia,
                Total = g.Count()
            })
            .OrderBy(x => x.Mes)
            .ThenBy(x => x.Tecnologia)
            .ToList();

        var model = new DashboardViewModel
        {
            TotalJobs = totalJobs,
            TotalTechnologies = totalTechnologies,
            TotalCompanies = totalCompanies,
            TopTechnologies = topTechnologies,
            SearchString = searchString,
            // JobsByMonth = jobsByMonth,
            QuantityTech = quantityTech,
            JobLocations = jobLocations,
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
