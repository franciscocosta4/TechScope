using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using TechScope.Data;
using TechScope.ViewModels;


namespace TechScope.Controllers;

public class JobsController : Controller
{

    private readonly ApplicationDbContext _context;

    public JobsController(ApplicationDbContext context)
    {
        _context = context;
    }


    public async Task<IActionResult> Index(string? searchString, int pageNumber = 1, int pageSize = 10)
    {
        var totalJobs = await _context.Jobs.CountAsync();

        var jobsByMonth = _context.Jobs  // grafico de vagas por mes do ano
            .Where(j => j.DatePosted.HasValue)
            .GroupBy(j => j.DatePosted.Value.Month)
            .Select(g => new jobsByMonthChartData
            {
                Mes = g.Key,
                Total = g.Count()
            })
            .OrderBy(x => x.Mes)
            .ToList();


        var RecentJobs = await _context.Jobs
            .OrderByDescending(x => x.DatePosted)
            .Take(20)
            .Select(j => new RecentJobsItem
            {
                Title = j.Title,
                ExternalId = j.ExternalId,
                DatePosted = j.DatePosted,
            })
            .ToListAsync();
        
        

        var model = new JobsViewModel
        {
            TotalJobs = totalJobs,
            RecentJobs = RecentJobs,
            SearchString = searchString,
            JobsByMonth = jobsByMonth,
            PageNumber = pageNumber,
            PageSize = pageSize
        };

        if (!string.IsNullOrWhiteSpace(searchString))
        {
            var term = searchString.Trim();

            model.ResultsCounter = _context.Jobs.Where(j => j.Title != null && j.Title.ToUpper().Contains(term.ToUpper())).Count();

            model.SearchResults = await _context.Jobs
                .Where(j => j.Title != null &&
                            j.Title.ToUpper().Contains(term.ToUpper()))
                .Select(j => new JobsSearchResult
                {
                    Title = j.Title!,
                    ExternalId = j.ExternalId,
                    DatePosted = j.DatePosted,
                    CompanyName = j.Company.Name,
                    Keywords = j.Keywords.Select(k => k.Keyword).ToList()
                })
                .OrderByDescending(x => x.DatePosted)
                .Skip((pageNumber - 1) * pageSize)
                .Take(pageSize)
                .ToListAsync();
        }
        return View(model);
    }



}
