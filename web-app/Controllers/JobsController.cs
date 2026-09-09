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


    public async Task<IActionResult> Index(string? searchString, string? Seniority,string? WorkModel, List<string> Locations, int pageNumber = 1, int pageSize = 10)
    {
        var totalJobs = await _context.Jobs.CountAsync();

        var JobsByDay = _context.Jobs 
            .Where(j => j.DatePosted.HasValue)
            .GroupBy(j => j.DatePosted.Value)
            .Select(g => new jobsByDayChartData
            {
                Data = g.Key,
                Total = g.Count()
            })
            .OrderBy(x => x.Data)
            .ToList();


        var RecentJobs = await _context.Jobs
            .Where(x => x.DatePosted != null) // assim evitamos vagas do indeed, q nao tem data
            .OrderByDescending(x => x.DatePosted)
            .Take(20)
            .Select(j => new RecentJobsItem
            {
                Title = j.Title,
                ExternalId = j.ExternalId,
                DatePosted = j.DatePosted,
            })
            .ToListAsync();
        
        var jobLocations =  _context.Jobs //pega em todas as locations registadas na base de dados
            .Select(job => job.Location)
            .Distinct()
            .ToList();
        
        var model = new JobsViewModel
        {
            TotalJobs = totalJobs,
            RecentJobs = RecentJobs,
            JobLocations = jobLocations,
            SearchString = searchString,
            Seniority = Seniority,
            WorkModel = WorkModel,
            Locations = Locations ?? new List<string>(),
            JobsByDay = JobsByDay,
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

            if (model.Locations != null && model.Locations.Any()) 
            {
                // pegamos nos termos de locations na url
                var locationTerms = model.Locations
                    .Where(x => !string.IsNullOrWhiteSpace(x))
                    .Select(x => x.Trim().ToUpper())
                    .ToList();

                if (locationTerms.Any())
                {
                    query = query.Where(j =>
                        j.Location != null &&
                        locationTerms.Any(location => j.Location.ToUpper().Contains(location))); // verfificamos se existem vagas com algum dos termos 
                }
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
