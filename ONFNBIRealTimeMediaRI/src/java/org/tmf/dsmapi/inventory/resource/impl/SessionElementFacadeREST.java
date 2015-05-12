/*
 * To change this template, choose Tools | Templates
 * and open the template in the editor.
 */
package org.tmf.dsmapi.inventory.resource.impl;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Set;
import javax.ejb.EJB;
import javax.ejb.Stateless;
import javax.ws.rs.Consumes;
import javax.ws.rs.DELETE;
import javax.ws.rs.GET;
import javax.ws.rs.POST;
import javax.ws.rs.Path;
import javax.ws.rs.PathParam;
import javax.ws.rs.Produces;
import javax.ws.rs.core.Context;
import javax.ws.rs.core.MultivaluedMap;
import javax.ws.rs.core.Response;
import javax.ws.rs.core.UriInfo;
import org.codehaus.jackson.node.ObjectNode;
import org.tmf.dsmapi.inventory.resource.model.SessionElement;
import org.tmf.dsmapi.common.exceptions.BadUsageException;
import org.tmf.dsmapi.common.impl.FacadeRestUtil;
import org.tmf.dsmapi.common.impl.PATCH;
import com.wordnik.swagger.annotations.*;
import java.lang.reflect.Array;
import java.lang.reflect.Field;
import javax.ws.rs.HEAD;
import javax.ws.rs.QueryParam;
import javax.ws.rs.core.Response.ResponseBuilder;
import org.tmf.dsmapi.common.model.Href;
import org.tmf.dsmapi.common.model.JsonPatch;

/**
 *
 * @author pierregauthier
 */
@Stateless
@Api(value = "/sessionElement", description = "Used to retrieve and manage SessionElement in inventory.")
@Path("/sessionElement")
public class SessionElementFacadeREST {

    @EJB
    private SessionElementFacade manager;

    public SessionElementFacadeREST() {
    }

    @GET
    @ApiOperation(value = "Retrieve SessionElement", notes = "Retrieve SessionElement using option filter.", response = SessionElement.class)
    @ApiResponses(value = {
        @ApiResponse(code = 200, message = "OK"),
        @ApiResponse(code = 400, message = "Invalid Filter"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Produces({"application/json"})
    public Response findByCriteriaWithFields(
            @ApiParam(value = "Query Specification", required = false) @QueryParam("_s") String _s,
            @ApiParam(value = "Field Specification", required = false) @QueryParam("fields") String fields,
            @Context UriInfo info) throws BadUsageException {
        // search criteria
        MultivaluedMap<String, String> criteria = info.getQueryParameters();
        // fields to filter view
        Set<String> fieldSet = FacadeRestUtil.getFieldSet(criteria);
        if (criteria.containsKey("_s"))
        {
            String[] stuff = criteria.getFirst("_s").split("=");
            String query = new String("");
            for (int count = 1;count<stuff.length;count++)
            {
                query += "=";
                query += stuff[count];
            }
            criteria.clear();
            criteria.add(stuff[0],query);
        }
        List<SessionElement> resultList = findByCriteria(criteria);

        Response response;
        if (fieldSet.isEmpty() || fieldSet.contains(FacadeRestUtil.ALL_FIELDS)) {
            response = Response.ok(resultList).build();
        } else {
            fieldSet.add(FacadeRestUtil.ID_FIELD);
            List<ObjectNode> nodeList = new ArrayList<ObjectNode>();
            for (SessionElement productOffering : resultList) {
                ObjectNode node = FacadeRestUtil.createNodeViewWithFields(productOffering, fieldSet);
                nodeList.add(node);
            }
            response = Response.ok(nodeList).build();
        }
        return response;
    }

    @POST
    @ApiOperation(value = "Create SessionElement", notes = "Creates equipment given the passed in representation.", response = SessionElement.class)
    @ApiResponses(value = {
        @ApiResponse(code = 201, message = "Created"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Consumes({"application/json"})
    @Produces({"application/json"})
    public Response create(
            @ApiParam(value = "SessionElement to be created.", required = true) SessionElement entity,
            @Context UriInfo uriInfo) {
        entity.setId(null);
        manager.create(entity);
        entity.setId(entity.getId());
        Response response = Response.ok(entity).build();
        return response;
    }

    @HEAD
    @ApiOperation(value = "Retrieve the HTTP Header", notes = "Retrieve the HTTP header that would have been returned by the coresponding GET.")
    @ApiResponses(value = {
        @ApiResponse(code = 204, message = "No Data"),
        @ApiResponse(code = 400, message = "Invalid Filter"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Produces({"application/json"})
    public Response getHTTPHeadersForList(
            @ApiParam(value = "Query Specification", required = false) @QueryParam("_s") String _s,
            @ApiParam(value = "Field Specification", required = false) @QueryParam("fields") String fields,
            @Context UriInfo info) throws BadUsageException {
        // search criteria
        MultivaluedMap<String, String> criteria = info.getQueryParameters();

        List<SessionElement> resultList = findByCriteria(criteria);

        Response response;
        ResponseBuilder responseBuilder = Response.noContent();
        String start = new String();
        if (resultList.size() == 0) {
            start = "0";
        } else {
            start = "1";
        }
        responseBuilder.header("Content-Range", "items " + start + "-" + resultList.size() + "/" + manager.count());
        response = responseBuilder.build();
        return response;
    }

    @GET
    @ApiOperation(value = "Retrieve equipment by ID", notes = "Retrieves a specific equipment by ID.", response = SessionElement.class)
    @ApiResponses(value = {
        @ApiResponse(code = 200, message = "OK"),
        @ApiResponse(code = 404, message = "Not found"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Path("/{id}")
    @Produces({"application/json"})
    public Response findWithFields(
            @ApiParam(value = "SessionElement ID", required = true) @PathParam("id") String id,
            @ApiParam(value = "Field Specification", required = false) @QueryParam("fields") String fields,
            @Context UriInfo info) {
        // fields to filter view
        Set<String> fieldSet = FacadeRestUtil.getFieldSet(info.getQueryParameters());

        SessionElement p = manager.find(id);
        Response response;
        // if troubleTicket exists
        if (p != null) {
            // 200
            if (fieldSet.isEmpty() || fieldSet.contains(FacadeRestUtil.ALL_FIELDS)) {
                response = Response.ok(p).build();
            } else {
                fieldSet.add(FacadeRestUtil.ID_FIELD);
                ObjectNode node = FacadeRestUtil.createNodeViewWithFields(p, fieldSet);
                response = Response.ok(node).build();
            }
        } else {
            // 404 not found
            response = Response.status(Response.Status.NOT_FOUND).build();
        }
        return response;
    }

    @PATCH
    @ApiOperation(value = "Modify SessionElement", notes = "Modify the specified equipment.", response = SessionElement.class, httpMethod = "PATCH")
    @ApiResponses(value = {
        @ApiResponse(code = 200, message = "OK"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Path("/{id}")
    @Consumes({"application/json+patch"})
    @Produces({"application/json"})
    public Response edit(@ApiParam(value = "SessionElement ID", required = true) @PathParam("id") String id,
    JsonPatch patch) {
        Response response = null;
        SessionElement entity = manager.find(id);
        if (entity != null) {
            // 200
            manager.edit(entity);
            response = Response.ok(entity).build();
        } else {
            // 404 not found
            response = Response.status(404).build();
        }
        return response;
    }

    @DELETE
    @ApiOperation(value = "Delete the specified SessionElement", notes = "Delete the specified equipment.")
    @ApiResponses(value = {
        @ApiResponse(code = 204, message = "No Content"),
        @ApiResponse(code = 404, message = "Not found"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Path("/{id}")
    public Response remove(@ApiParam(value = "SessionElement ID", required = true) @PathParam("id") String id) {
        Response response = null;
       try {
            manager.remove(manager.find(id));
            response = Response.noContent().build();
        } catch (Exception ex) {
            response = Response.status(404).build();            
        }
        return response;
    }

    private List<SessionElement> findByCriteria(MultivaluedMap<String, String> criteria) throws BadUsageException {
        List<SessionElement> resultList = null;
        if (criteria != null && !criteria.isEmpty()) {
            resultList = manager.findByCriteria(criteria, SessionElement.class);
        } else {
            resultList = manager.findAll();
        }
        return resultList;
    }

    
    @HEAD
    @ApiOperation(value = "Retrieve the HTTP Header", notes = "Retrieve the HTTP header that would have been returned by the coresponding GET.")
    @ApiResponses(value = {
        @ApiResponse(code = 204, message = "No Data"),
        @ApiResponse(code = 400, message = "Invalid Filter"),
        @ApiResponse(code = 404, message = "Not found"),
        @ApiResponse(code = 500, message = "Internal Server Error")
    })
    @Path("/{id}")
    @Produces({"application/json"})
    public Response getHTTPHeadersForInstance(
            @ApiParam(value = "Query Specification", required = false) @QueryParam("_s") String _s,
            @ApiParam(value = "Field Specification", required = false) @QueryParam("fields") String fields,
            @Context UriInfo info) throws BadUsageException {
        // search criteria
        MultivaluedMap<String, String> criteria = info.getQueryParameters();

        List<SessionElement> resultList = findByCriteria(criteria);

        Response response;
        ResponseBuilder responseBuilder = Response.noContent();
        String start = new String();
        if (resultList.size() == 0) {
            start = "0";
        } else {
            start = "1";
        }
        responseBuilder.header("Content-Range", "items " + start + "-" + resultList.size() + "/" + manager.count());
        response = responseBuilder.build();
        return response;
    }
}
