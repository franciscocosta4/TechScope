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


    public async Task<IActionResult> Index(string? searchString, string? Seniority,string? WorkModel, int pageNumber = 1, int pageSize = 10)
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
            Seniority = Seniority,
            JobsByMonth = jobsByMonth,
            PageNumber = pageNumber,
            PageSize = pageSize
        };

        if (!string.IsNullOrWhiteSpace(searchString))
        {
            var term = searchString.Trim();
            
            // query base procura por titulos que contenham o termo
            var query = _context.Jobs.AsQueryable();
            query = query.Where(j => j.Title != null && j.Title.ToUpper().Contains(term.ToUpper()));

            if (!string.IsNullOrWhiteSpace(Seniority))
            {
                var SeniorityTerm = Seniority.Trim();

                query = query.Where(j =>
                    j.Keywords.Any(k =>k.Keyword != null && k.Keyword.ToUpper().Contains(SeniorityTerm.ToUpper())));
            } 

            if (!string.IsNullOrWhiteSpace(WorkModel))
            {
                var WorkModelTerm = WorkModel.Trim();

                query = query.Where(j =>
                    j.Keywords.Any(k =>k.Keyword != null && k.Keyword.ToUpper().Contains(WorkModelTerm.ToUpper())));
            } 

            // só conta depois de passar pelos filtros
            model.ResultsCounter = query.Count();

            model.SearchResults = await query
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
